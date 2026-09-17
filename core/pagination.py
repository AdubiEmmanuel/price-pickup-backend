from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    """Default list pagination: 25 per page, with an opt-in ?page_size= override
    (capped at max_page_size) for callers that need to page through everything."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 500
