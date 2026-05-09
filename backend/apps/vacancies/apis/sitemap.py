from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.vacancies.selectors import get_public_vacancies


class PublicVacancySitemapApi(APIView):
    """GET /api/public/vacancies/sitemap.xml — canonical public vacancy URLs."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> HttpResponse:
        site_url = settings.FRONTEND_URL.rstrip("/")
        vacancies = get_public_vacancies().order_by("-updated_at").values_list("id", "updated_at")[:50_000]
        items = [
            _url_item(
                loc=f"{site_url}/jobs/{vacancy_id}",
                lastmod=updated_at.isoformat(),
            )
            for vacancy_id, updated_at in vacancies
        ]
        body = '<?xml version="1.0" encoding="UTF-8"?>\n'
        body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        body += "".join(items)
        body += "</urlset>\n"
        return HttpResponse(body, content_type="application/xml")


def _url_item(*, loc: str, lastmod: str) -> str:
    return (
        "  <url>\n"
        f"    <loc>{escape(loc)}</loc>\n"
        f"    <lastmod>{escape(lastmod)}</lastmod>\n"
        "    <changefreq>daily</changefreq>\n"
        "    <priority>0.8</priority>\n"
        "  </url>\n"
    )
