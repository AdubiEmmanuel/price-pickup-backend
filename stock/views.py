import csv
import io
import secrets
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from competitors.choices import SKU_CATEGORY_CHOICES, SKU_SIZE_CHOICES, BRAND_CHOICES, MARKET_CHANNEL_CHOICES
from competitors.csv_utils import decode_csv_bytes
from competitors.models import CompetitorPrice
from competitors.serializers import CompetitorPriceSerializer
from .models import Distributor, Customer, CustomerStockEntry
from .serializers import DistributorSerializer, CustomerSerializer, CustomerStockEntrySerializer


CONFIRM_PHRASE = 'DELETE ALL'


def _require_clear_confirmation(request):
    """
    Shared guard for every destructive `clear` action: require the exact
    phrase in the body so a bulk-delete can't be triggered by an accidental
    click or a stray automated request. Returns an error Response, or None
    if the caller may proceed.
    """
    if request.data.get('confirm') != CONFIRM_PHRASE:
        return Response(
            {"error": f'Send {{"confirm": "{CONFIRM_PHRASE}"}} to confirm this irreversible action.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


def _period_boundaries():
    """Today/week/month/year start boundaries (server-local via Django's active timezone)."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)
    return now, today_start, week_start, month_start, year_start


class DistributorViewSet(viewsets.ModelViewSet):
    """
    Distributor master data: the business partner supplying a set of stores
    within a city. Sits above Customer (the store) in the real hierarchy.
    """
    queryset = Distributor.objects.all()
    serializer_class = DistributorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city']
    search_fields = ['distributor_code', 'distributor_name', 'city']
    ordering_fields = ['city', 'distributor_name', 'distributor_code', 'created_at']

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Typeahead by code, name, or city."""
        q = request.query_params.get('q', '').strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(Q(distributor_code__icontains=q) | Q(distributor_name__icontains=q) | Q(city__icontains=q))
        rows = qs.values('distributor_code', 'distributor_name', 'city')[:50]
        return Response(list(rows), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Bulk-load/refresh the distributor roster from a CSV with columns:
        Distributor Code, Distributor Name, City. Upserts by Distributor
        Code so re-uploading a refreshed roster is safe.
        """
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({"error": "File must be CSV format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = decode_csv_bytes(file.read())
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            return Response({"error": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        headers = reader.fieldnames
        if not headers or 'Distributor Code' not in headers:
            return Response(
                {"error": "CSV format is invalid - Distributor Code column not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        updated_count = 0
        error_rows = []
        for row_num, row in enumerate(reader, start=2):
            code = (row.get('Distributor Code') or '').strip()
            name = (row.get('Distributor Name') or '').strip()
            city = (row.get('City') or '').strip()
            if not code or not name:
                error_rows.append({'row': row_num, 'errors': 'Distributor Code and Distributor Name are required'})
                continue
            try:
                obj, was_created = Distributor.objects.update_or_create(
                    distributor_code=code,
                    defaults={'distributor_name': name, 'city': city},
                )
                created_count += 1 if was_created else 0
                updated_count += 0 if was_created else 1
            except Exception as e:
                error_rows.append({'row': row_num, 'errors': str(e)})

        return Response({
            'message': f'Created {created_count}, updated {updated_count} distributors',
            'errors': error_rows if error_rows else None,
        }, status=status.HTTP_201_CREATED if (created_count or updated_count) else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Wipe the entire distributor roster - for recovering from a bad bulk
        upload. Distributor rows are protected against deletion while stores
        still reference them, so clearing distributors necessarily clears
        all stores (and, transitively, their stock history) too.
        """
        error = _require_clear_confirmation(request)
        if error:
            return error
        with transaction.atomic():
            stock_count, _ = CustomerStockEntry.objects.all().delete()
            customer_count, _ = Customer.objects.all().delete()
            distributor_count, _ = Distributor.objects.all().delete()
        return Response(
            {'message': f'Deleted {distributor_count} distributors, {customer_count} stores, and {stock_count} stock entries'},
            status=status.HTTP_200_OK,
        )


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Store/customer master data: loaded up front by an admin (one at a time
    or via CSV bulk upload), then selected - not typed - by salesmen.
    """
    queryset = Customer.objects.select_related('distributor').all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location', 'distributor']
    search_fields = ['customer_code', 'customer_name', 'location']
    ordering_fields = ['customer_name', 'customer_code', 'created_at']

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Typeahead for the salesman's store picker, by code or name."""
        q = request.query_params.get('q', '').strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(Q(customer_code__icontains=q) | Q(customer_name__icontains=q))
        rows = qs.values('customer_code', 'customer_name', 'location')[:50]
        return Response(list(rows), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Bulk-load/refresh the store roster from a CSV with columns:
        Customer Code, Customer Name, Location, Distributor Code. Upserts by
        Customer Code so re-uploading a refreshed roster is safe. The
        distributor must already exist (add distributors first).
        """
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({"error": "File must be CSV format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = decode_csv_bytes(file.read())
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            return Response({"error": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        headers = reader.fieldnames
        if not headers or 'Customer Code' not in headers:
            return Response(
                {"error": "CSV format is invalid - Customer Code column not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        updated_count = 0
        error_rows = []
        for row_num, row in enumerate(reader, start=2):
            code = (row.get('Customer Code') or '').strip()
            name = (row.get('Customer Name') or '').strip()
            location = (row.get('Location') or '').strip()
            distributor_code = (row.get('Distributor Code') or '').strip()
            channel = (row.get('Channel') or '').strip() or None
            if not code or not name:
                error_rows.append({'row': row_num, 'errors': 'Customer Code and Customer Name are required'})
                continue
            if channel and channel not in dict(MARKET_CHANNEL_CHOICES):
                valid = ', '.join(dict(MARKET_CHANNEL_CHOICES).keys())
                error_rows.append({'row': row_num, 'errors': f'Invalid Channel "{channel}". Must be one of: {valid}'})
                continue
            distributor = None
            if distributor_code:
                try:
                    distributor = Distributor.objects.get(distributor_code=distributor_code)
                except Distributor.DoesNotExist:
                    error_rows.append({'row': row_num, 'errors': f'No distributor with code "{distributor_code}" - add it first'})
                    continue
            defaults = {'customer_name': name, 'location': location, 'distributor': distributor}
            if channel:
                # Only set when the CSV actually has a value - a re-upload of
                # a roster without a Channel column shouldn't blank out a
                # channel already set some other way.
                defaults['channel'] = channel
            try:
                obj, was_created = Customer.objects.update_or_create(
                    customer_code=code,
                    defaults=defaults,
                )
                created_count += 1 if was_created else 0
                updated_count += 0 if was_created else 1
            except Exception as e:
                error_rows.append({'row': row_num, 'errors': str(e)})

        return Response({
            'message': f'Created {created_count}, updated {updated_count} customers',
            'errors': error_rows if error_rows else None,
        }, status=status.HTTP_201_CREATED if (created_count or updated_count) else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Wipe the entire store roster - for recovering from a bad bulk upload.
        Customer rows are protected against deletion while stock entries
        still reference them, so clearing customers necessarily clears all
        stock history too; the confirmation message says so up front.
        """
        error = _require_clear_confirmation(request)
        if error:
            return error
        with transaction.atomic():
            stock_count, _ = CustomerStockEntry.objects.all().delete()
            customer_count, _ = Customer.objects.all().delete()
        return Response(
            {'message': f'Deleted {customer_count} customers and {stock_count} stock entries'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'])
    def quick_create(self, request):
        """
        One-call "Create New Store" flow for a salesman who finds a new
        store in the field: creates the store (auto-generating its code),
        then for each product logs its opening stock and/or saves its
        Case/Unit price - all in a single request instead of separate trips
        through the Customers, Customer Stock, and Price Pickup screens.

        Expected payload:
        {
            "distributor_code": "LAG01",
            "customer_name": "Mama Ngozi Stores",
            "phone_number": "08012345678",       (optional)
            "location": "Ikeja, Lagos",           (optional)
            "channel": "OPEN_MARKET",             (optional - one of Customer.channel's choices)
            "store_image": "data:image/jpeg;...", (optional, see Customer.store_image)
            "products": [
                {"sku_category": "NUTRITION", "brand": "KNORR", "sku_name": "Royco Mandara",
                 "sku_size": "REGULAR PACK", "is_unilever": true,
                 "current_stock": 20, "sales_in": 20,
                 "kd_case": 15000, "kd_unit": null, "units_per_case": 24},  (price fields optional)
                ...
            ]
        }
        """
        data = request.data
        distributor_code = data.get('distributor_code')
        customer_name = (data.get('customer_name') or '').strip()
        if not distributor_code or not customer_name:
            return Response({'error': 'distributor_code and customer_name are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            distributor = Distributor.objects.get(distributor_code=distributor_code)
        except Distributor.DoesNotExist:
            return Response({'error': f'No distributor with code "{distributor_code}"'}, status=status.HTTP_400_BAD_REQUEST)

        channel = data.get('channel') or None
        if channel and channel not in dict(MARKET_CHANNEL_CHOICES):
            valid = ', '.join(dict(MARKET_CHANNEL_CHOICES).keys())
            return Response({'error': f'Invalid channel "{channel}". Must be one of: {valid}'}, status=status.HTTP_400_BAD_REQUEST)

        store_image = data.get('store_image') or None
        if store_image and len(store_image) > 2_000_000:
            return Response({'error': 'Image is too large - please use a smaller photo.'}, status=status.HTTP_400_BAD_REQUEST)

        products = data.get('products') or []
        if not isinstance(products, list):
            return Response({'error': 'products must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        # Auto-generate a unique customer_code - a salesman creating a store
        # on the spot has no ERP code to give it.
        customer_code = None
        for _ in range(10):
            candidate = f"{distributor.distributor_code}-{secrets.token_hex(3).upper()}"
            if not Customer.objects.filter(customer_code=candidate).exists():
                customer_code = candidate
                break
        if not customer_code:
            return Response({'error': 'Could not generate a unique store code - please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        customer = Customer.objects.create(
            customer_code=customer_code,
            customer_name=customer_name,
            location=data.get('location') or '',
            phone_number=data.get('phone_number') or None,
            store_image=store_image,
            channel=channel,
            distributor=distributor,
        )

        stock_created = 0
        prices_saved = 0
        errors = []

        for index, item in enumerate(products):
            sku_name = (item.get('sku_name') or '').strip()
            sku_category = item.get('sku_category')
            brand = item.get('brand') or None
            if not sku_name or not sku_category:
                errors.append({'index': index, 'error': 'sku_name and sku_category are required'})
                continue

            entry_serializer = CustomerStockEntrySerializer(data={
                'customer_code': customer_code,
                'sku_category': sku_category,
                'sku_size': item.get('sku_size'),
                'brand': brand,
                'sku_name': sku_name,
                'current_stock': item.get('current_stock'),
                'sales_in': item.get('sales_in'),
                'is_unilever': item.get('is_unilever', False),
                'source': 'FORM',
            })
            if entry_serializer.is_valid():
                entry_serializer.save()
                stock_created += 1
            else:
                errors.append({'index': index, 'error': entry_serializer.errors})
                continue

            # Price is optional - only touch the catalog when at least one
            # price field was actually supplied for this product.
            kd_case = item.get('kd_case')
            kd_unit = item.get('kd_unit')
            units_per_case = item.get('units_per_case')
            if kd_case is None and kd_unit is None and units_per_case is None:
                continue

            price_data = {k: v for k, v in {
                'kd_case': kd_case, 'kd_unit': kd_unit, 'units_per_case': units_per_case,
            }.items() if v is not None}

            existing_price = (
                CompetitorPrice.objects.filter(sku_name=sku_name, brand=brand)
                .order_by('-created_at').first()
            )
            if existing_price:
                price_serializer = CompetitorPriceSerializer(existing_price, data=price_data, partial=True)
            else:
                price_data.update({
                    'sku_name': sku_name, 'brand': brand, 'sku_category': sku_category,
                    'sku_size': item.get('sku_size'), 'is_unilever': item.get('is_unilever', False),
                    'source': 'FORM',
                })
                price_serializer = CompetitorPriceSerializer(data=price_data)

            if price_serializer.is_valid():
                price_serializer.save()
                prices_saved += 1
            else:
                errors.append({'index': index, 'error': price_serializer.errors})

        return Response({
            'customer': CustomerSerializer(customer).data,
            'stock_entries_created': stock_created,
            'prices_saved': prices_saved,
            'errors': errors,
        }, status=status.HTTP_201_CREATED)


class CustomerStockViewSet(viewsets.ModelViewSet):
    queryset = CustomerStockEntry.objects.select_related('customer').all()
    serializer_class = CustomerStockEntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sku_category', 'brand', 'is_unilever']
    search_fields = ['customer__customer_name', 'customer__customer_code', 'sku_name', 'brand', 'customer__location']
    ordering_fields = ['created_at', 'current_stock', 'sales_in']

    @action(detail=False, methods=['get'])
    def get_category_choices(self, request):
        return Response({
            'sku_categories': dict(SKU_CATEGORY_CHOICES),
            'sku_sizes': dict(SKU_SIZE_CHOICES),
            'brands': dict(BRAND_CHOICES),
        })

    @action(detail=False, methods=['get'])
    def distinct_skus(self, request):
        """
        Every distinct SKU already recorded across any store - populates the
        Category -> Brand -> SKU -> Size picker when a salesman logs a
        product that's new to THIS store but already tracked elsewhere,
        instead of having them retype its attributes freehand.

        Deduplicates by (sku_name, brand, sku_category, sku_size) only -
        is_unilever is taken from that combo's most recent entry rather than
        included in the distinct key, so an inconsistent older is_unilever
        value on the same SKU can't produce a duplicate catalog row.
        """
        entries = (
            CustomerStockEntry.objects
            .order_by('-created_at')
            .values('sku_name', 'brand', 'sku_category', 'sku_size', 'is_unilever')
        )
        seen = set()
        results = []
        for e in entries:
            key = (e['sku_name'], e['brand'], e['sku_category'], e['sku_size'])
            if key in seen:
                continue
            seen.add(key)
            results.append(e)
        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def current_stock(self, request):
        """
        Latest known entry per product at one store - what the salesman's
        POS screen shows before they enter anything, so they see what's
        already there instead of blind-guessing a starting stock every visit.
        """
        customer_code = request.query_params.get('customer_code')
        if not customer_code:
            return Response({"error": "customer_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        entries = (
            CustomerStockEntry.objects
            .filter(customer__customer_code=customer_code)
            .order_by('-created_at')
        )
        latest_by_product = {}
        for e in entries:
            key = (e.sku_name, e.brand)
            if key not in latest_by_product:
                latest_by_product[key] = e

        results = [{
            'sku_name': e.sku_name,
            'brand': e.brand,
            'sku_category': e.sku_category,
            'sku_size': e.sku_size,
            'is_unilever': e.is_unilever,
            'current_stock': e.current_stock,
            'last_updated': e.created_at,
        } for e in latest_by_product.values()]
        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def submit_visit(self, request):
        """
        "Checkout" endpoint for the POS-style form: one customer_code (the
        salesman must have picked a real store) plus a cart of per-SKU line
        items, created together.
        Expected payload:
        {
            "customer_code": "STR001",
            "items": [
                {"sku_category": "...", "sku_size": "...", "brand": "...",
                 "sku_name": "...", "current_stock": 12, "sales_in": 5,
                 "is_unilever": true},
                ...
            ]
        }
        """
        data = request.data
        customer_code = data.get('customer_code')
        items = data.get('items')

        try:
            customer = Customer.objects.get(customer_code=customer_code) if customer_code else None
        except Customer.DoesNotExist:
            customer = None
        if not customer_code:
            return Response({"error": "customer_code is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not customer:
            return Response(
                {"error": f'No customer with code "{customer_code}". Ask an admin to add it first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not items or not isinstance(items, list):
            return Response({"error": "items must be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []

        with transaction.atomic():
            for index, item in enumerate(items):
                entry_data = {**item, 'customer_code': customer_code, 'source': 'FORM'}

                # Running ledger: if the caller only sent sales_in (the normal
                # case once the salesman is looking at current_stock() output
                # instead of blind-guessing it), compute the new total from
                # the last known stock for this exact product at this store.
                if entry_data.get('current_stock') is None and entry_data.get('sales_in') is not None:
                    previous = (
                        CustomerStockEntry.objects
                        .filter(customer=customer, sku_name=entry_data.get('sku_name'), brand=entry_data.get('brand'))
                        .order_by('-created_at')
                        .first()
                    )
                    previous_stock = previous.current_stock if previous and previous.current_stock else 0
                    entry_data['current_stock'] = previous_stock + int(entry_data['sales_in'])

                serializer = self.get_serializer(data=entry_data)
                if serializer.is_valid():
                    serializer.save()
                    created.append(serializer.data)
                else:
                    errors.append({'index': index, 'errors': serializer.errors})

        response_status = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response({'created': created, 'errors': errors}, status=response_status)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Wipe all recorded stock/sales-in visits - for recovering from bad
        salesman input or a bad bulk import - without touching the customer
        roster itself.
        """
        error = _require_clear_confirmation(request)
        if error:
            return error
        count, _ = CustomerStockEntry.objects.all().delete()
        return Response({'message': f'Deleted {count} stock entries'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Store-centric payload for the Regional Manager dashboard: every
        store (even ones with no visits yet) with its products broken down
        by Today/WTD/MTD/YTD sales-in and current stock, plus alerts,
        store rankings, and a trend series for the graph view over a
        caller-selected date range.
        """
        params = request.query_params
        low_stock_threshold = int(params.get('low_stock_threshold', 5))
        stale_days = int(params.get('stale_days', 14))
        customer_code = params.get('customer_code')
        location = params.get('location')

        now, today_start, week_start, month_start, year_start = _period_boundaries()
        stale_cutoff = now - timedelta(days=stale_days)

        start_date_param = params.get('start_date')
        end_date_param = params.get('end_date')
        end_date = (
            datetime.strptime(end_date_param, '%Y-%m-%d').replace(tzinfo=now.tzinfo) + timedelta(days=1)
            if end_date_param else now
        )
        start_date = (
            datetime.strptime(start_date_param, '%Y-%m-%d').replace(tzinfo=now.tzinfo)
            if start_date_param else now - timedelta(days=30)
        )

        customers_qs = Customer.objects.all()
        if customer_code:
            customers_qs = customers_qs.filter(customer_code=customer_code)
        if location:
            customers_qs = customers_qs.filter(location__icontains=location)
        customers = list(customers_qs)

        all_entries = list(
            CustomerStockEntry.objects
            .select_related('customer')
            .filter(customer__in=customers)
            .order_by('-created_at')
        )

        entries_by_customer = {}
        for e in all_entries:
            entries_by_customer.setdefault(e.customer_id, []).append(e)

        def sum_since(entries, since):
            return sum(e.sales_in or 0 for e in entries if e.created_at >= since)

        stores = []
        alerts = []
        ranking_rows = []

        for customer in customers:
            entries = entries_by_customer.get(customer.id, [])  # newest first
            product_groups = {}
            for e in entries:
                product_groups.setdefault((e.sku_name, e.brand), []).append(e)

            products = []
            totals = {'current_stock': 0, 'sales_today': 0, 'sales_wtd': 0, 'sales_mtd': 0, 'sales_ytd': 0}

            for (sku_name, brand), prod_entries in product_groups.items():
                latest = prod_entries[0]
                sales_today = sum_since(prod_entries, today_start)
                sales_wtd = sum_since(prod_entries, week_start)
                sales_mtd = sum_since(prod_entries, month_start)
                sales_ytd = sum_since(prod_entries, year_start)

                products.append({
                    'sku_name': sku_name,
                    'brand': brand,
                    'sku_category': latest.sku_category,
                    'current_stock': latest.current_stock,
                    'sales_today': sales_today,
                    'sales_wtd': sales_wtd,
                    'sales_mtd': sales_mtd,
                    'sales_ytd': sales_ytd,
                })
                totals['current_stock'] += latest.current_stock or 0
                totals['sales_today'] += sales_today
                totals['sales_wtd'] += sales_wtd
                totals['sales_mtd'] += sales_mtd
                totals['sales_ytd'] += sales_ytd

                alert_base = {
                    'customer_code': customer.customer_code,
                    'customer_name': customer.customer_name,
                    'location': customer.location,
                    'sku_name': sku_name,
                    'brand': brand,
                    'current_stock': latest.current_stock,
                    'last_updated': latest.created_at,
                }
                if latest.current_stock is not None and latest.current_stock <= low_stock_threshold:
                    alerts.append({**alert_base, 'reason': 'LOW_STOCK'})
                if latest.created_at < stale_cutoff:
                    alerts.append({**alert_base, 'reason': 'NO_MOVEMENT'})

            stores.append({
                'customer_code': customer.customer_code,
                'customer_name': customer.customer_name,
                'location': customer.location,
                'products': products,
                'totals': totals,
            })
            ranking_rows.append({
                'customer_code': customer.customer_code,
                'customer_name': customer.customer_name,
                'location': customer.location,
                'sales_mtd': totals['sales_mtd'],
                'current_stock': totals['current_stock'],
            })

        by_sales_mtd = sorted(ranking_rows, key=lambda r: r['sales_mtd'], reverse=True)
        by_current_stock = sorted(ranking_rows, key=lambda r: r['current_stock'], reverse=True)
        rankings = {
            'top_by_sales_mtd': by_sales_mtd[:5],
            'bottom_by_sales_mtd': by_sales_mtd[-5:][::-1] if len(by_sales_mtd) > 5 else by_sales_mtd[::-1],
            'top_by_current_stock': by_current_stock[:5],
            'bottom_by_current_stock': by_current_stock[-5:][::-1] if len(by_current_stock) > 5 else by_current_stock[::-1],
        }

        # Trends: entries within the caller-selected range, for the graph view
        windowed_entries = [e for e in all_entries if start_date <= e.created_at <= end_date]
        windowed_entries.sort(key=lambda e: e.created_at)

        trend_groups = {}
        for e in windowed_entries:
            trend_groups.setdefault((e.customer_id, e.sku_name, e.brand), []).append(e)

        days_span = max(1, (end_date - start_date).days)
        trends = []
        for (customer_id, sku_name, brand), grp in trend_groups.items():
            customer = grp[0].customer
            total_sales_in = sum(e.sales_in or 0 for e in grp)
            trends.append({
                'customer_code': customer.customer_code,
                'customer_name': customer.customer_name,
                'location': customer.location,
                'sku_name': sku_name,
                'brand': brand,
                'total_sales_in': total_sales_in,
                'avg_daily_sales_in': round(total_sales_in / days_span, 2),
                'points': [
                    {'date': e.created_at, 'current_stock': e.current_stock, 'sales_in': e.sales_in}
                    for e in grp
                ],
            })

        return Response({
            'stores': stores,
            'alerts': alerts,
            'rankings': rankings,
            'trends': trends,
        })
