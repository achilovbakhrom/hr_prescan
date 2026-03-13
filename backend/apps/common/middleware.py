from django.http import HttpRequest, HttpResponse


class CompanyMiddleware:
    """Attach request.company for authenticated HR/admin users."""

    def __init__(self, get_response: object) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.company = None  # type: ignore[attr-defined]

        if hasattr(request, "user") and request.user.is_authenticated:
            user = request.user
            if hasattr(user, "role") and user.role in ("admin", "hr") and user.company_id is not None:
                request.company = user.company  # type: ignore[attr-defined]

        return self.get_response(request)  # type: ignore[operator]
