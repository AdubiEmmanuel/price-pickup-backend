from datetime import timedelta

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES, BRAND_CHOICES
from .models import CustomerStockEntry
from .serializers import CustomerStockEntrySerializer


def _group_key(entry):
    return (entry.customer_name, entry.location, entry.sku_name, entry.brand)


class CustomerStockViewSet(viewsets.ModelViewSet):
    queryset = CustomerStockEntry.objects.all()
    serializer_class = CustomerStockEntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_name', 'location', 'sku_category', 'brand', 'is_unilever']
    search_fields = ['customer_name', 'sku_name', 'brand', 'location']
    ordering_fields = ['created_at', 'current_stock', 'sales_in']

    @action(detail=False, methods=['get'])
    def get_category_choices(self, request):
        return Response({
            'sku_categories': dict(SKU_CATEGORY_CHOICES),
            'sku_sizes': dict(SKU_SIZE_CHOICES),
            'brands': dict(BRAND_CHOICES),
        })

    @action(detail=False, methods=['get'])
    def search_customers(self, request):
        """
        Lightweight autocomplete for customer name + location, so salesmen
        re-use the same customer identity instead of retyping it each visit.
        """
        q = request.query_params.get('q', '').strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(Q(customer_name__icontains=q) | Q(location__icontains=q))
        # Clear the model's default ordering (-created_at) - otherwise Postgres
        # can't collapse rows to DISTINCT on customer_name/location alone.
        rows = qs.order_by().values('customer_name', 'location').distinct()[:50]
        return Response(list(rows), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def submit_visit(self, request):
        """
        "Checkout" endpoint for the POS-style form: one customer_name +
        location, plus a cart of per-SKU line items, created together.
        Expected payload:
        {
            "customer_name": "...", "location": "...",
            "items": [
                {"sku_category": "...", "sku_size": "...", "brand": "...",
                 "sku_name": "...", "current_stock": 12, "sales_in": 5,
                 "is_unilever": true},
                ...
            ]
        }
        """
        data = request.data
        customer_name = data.get('customer_name')
        location = data.get('location')
        items = data.get('items')

        if not customer_name or not location:
            return Response(
                {"error": "customer_name and location are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not items or not isinstance(items, list):
            return Response(
                {"error": "items must be a non-empty list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = []
        errors = []

        with transaction.atomic():
            for index, item in enumerate(items):
                entry_data = {
                    **item,
                    'customer_name': customer_name,
                    'location': location,
                    'source': 'FORM',
                }
                serializer = self.get_serializer(data=entry_data)
                if serializer.is_valid():
                    serializer.save()
                    created.append(serializer.data)
                else:
                    errors.append({'index': index, 'errors': serializer.errors})

        response_status = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response({'created': created, 'errors': errors}, status=response_status)

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Aggregated payload for the Regional Manager dashboard: latest
        per-customer/SKU snapshot, low-stock/no-movement alerts, trend data
        over the requested window, and customer rankings.
        """
        params = request.query_params
        days = int(params.get('days', 30))
        low_stock_threshold = int(params.get('low_stock_threshold', 5))
        stale_days = int(params.get('stale_days', 14))

        qs = self.filter_queryset(self.get_queryset())

        now = timezone.now()
        window_start = now - timedelta(days=days)
        stale_cutoff = now - timedelta(days=stale_days)

        all_entries = list(qs.order_by('-created_at'))

        # Latest entry per (customer, location, sku_name, brand) - entries are
        # already ordered newest-first, so the first time we see a key wins.
        latest_by_key = {}
        for entry in all_entries:
            key = _group_key(entry)
            if key not in latest_by_key:
                latest_by_key[key] = entry

        latest_snapshot = []
        alerts = []
        for entry in latest_by_key.values():
            snapshot = {
                'customer_name': entry.customer_name,
                'location': entry.location,
                'sku_name': entry.sku_name,
                'brand': entry.brand,
                'sku_category': entry.sku_category,
                'current_stock': entry.current_stock,
                'sales_in': entry.sales_in,
                'last_updated': entry.created_at,
            }
            latest_snapshot.append(snapshot)

            if entry.current_stock is not None and entry.current_stock <= low_stock_threshold:
                alerts.append({**snapshot, 'reason': 'LOW_STOCK'})
            if entry.created_at < stale_cutoff:
                alerts.append({**snapshot, 'reason': 'NO_MOVEMENT'})

        # Trends: entries within the window, grouped by customer+SKU, oldest first
        windowed_entries = [e for e in all_entries if e.created_at >= window_start]
        windowed_entries.sort(key=lambda e: e.created_at)

        trend_groups = {}
        for entry in windowed_entries:
            key = _group_key(entry)
            trend_groups.setdefault(key, []).append(entry)

        trends = []
        for (customer_name, location, sku_name, brand), entries in trend_groups.items():
            total_sales_in = sum(e.sales_in or 0 for e in entries)
            trends.append({
                'customer_name': customer_name,
                'location': location,
                'sku_name': sku_name,
                'brand': brand,
                'total_sales_in': total_sales_in,
                'avg_daily_sales_in': round(total_sales_in / days, 2) if days else 0,
                'points': [
                    {
                        'date': e.created_at,
                        'current_stock': e.current_stock,
                        'sales_in': e.sales_in,
                    }
                    for e in entries
                ],
            })

        # Rankings: total sales_in and current_stock per customer within the window
        customer_totals = {}
        for entry in windowed_entries:
            ckey = (entry.customer_name, entry.location)
            totals = customer_totals.setdefault(ckey, {'sales_in': 0, 'current_stock': 0})
            totals['sales_in'] += entry.sales_in or 0

        # Use latest snapshot (not the summed window) for current stock per customer
        for entry in latest_by_key.values():
            ckey = (entry.customer_name, entry.location)
            if ckey in customer_totals:
                customer_totals[ckey]['current_stock'] += entry.current_stock or 0

        ranking_rows = [
            {'customer_name': name, 'location': loc, **totals}
            for (name, loc), totals in customer_totals.items()
        ]
        by_sales_in = sorted(ranking_rows, key=lambda r: r['sales_in'], reverse=True)
        by_current_stock = sorted(ranking_rows, key=lambda r: r['current_stock'], reverse=True)

        rankings = {
            'top_by_sales_in': by_sales_in[:5],
            'bottom_by_sales_in': by_sales_in[-5:][::-1] if len(by_sales_in) > 5 else by_sales_in[::-1],
            'top_by_current_stock': by_current_stock[:5],
            'bottom_by_current_stock': by_current_stock[-5:][::-1] if len(by_current_stock) > 5 else by_current_stock[::-1],
        }

        return Response({
            'latest_snapshot': latest_snapshot,
            'alerts': alerts,
            'trends': trends,
            'rankings': rankings,
        })
