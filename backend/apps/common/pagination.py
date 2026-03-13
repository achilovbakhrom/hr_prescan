from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Standard pagination with page size of 20 and max of 100."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
