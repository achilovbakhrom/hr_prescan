from __future__ import annotations

import gzip
import os
import pathlib
import shutil
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from datetime import UTC, datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

URL_TEMPLATE = "https://download.db-ip.com/free/dbip-country-lite-{ym}.mmdb.gz"


class Command(BaseCommand):
    help = "Download the DB-IP Lite Country MMDB to GEOIP2_DB_PATH."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--max-age-days",
            type=int,
            default=30,
            help="Skip download if the existing DB is younger than this (default 30).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Download even if the DB exists and is fresh.",
        )

    def handle(self, *args: object, **options: object) -> None:
        db_path = getattr(settings, "GEOIP2_DB_PATH", "")
        if not db_path:
            self.stdout.write("GEOIP2_DB_PATH not configured — skipping download.")
            return

        target = pathlib.Path(db_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not options["force"]:
            age_days = (time.time() - target.stat().st_mtime) / 86400
            if age_days < options["max_age_days"]:
                self.stdout.write(
                    f"GeoIP DB is fresh ({age_days:.1f}d < {options['max_age_days']}d) — skipping."
                )
                return

        try:
            self._download(target)
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(f"[WARN] GeoIP download failed: {exc} — continuing without DB.")

    def _download(self, target: pathlib.Path) -> None:
        for ym in _candidate_year_months():
            url = URL_TEMPLATE.format(ym=ym)
            self.stdout.write(f"Trying {url}...")
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
                    self._stream_to_target(resp, target)
                self.stdout.write(self.style.SUCCESS(f"GeoIP DB written to {target}"))
                return
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    continue
                raise
        raise RuntimeError("No DB-IP Lite MMDB available for current or previous month.")

    def _stream_to_target(self, resp: object, target: pathlib.Path) -> None:
        with tempfile.NamedTemporaryFile(suffix=".gz", delete=False) as tmp_gz:
            shutil.copyfileobj(resp, tmp_gz)  # type: ignore[arg-type]
            gz_path = tmp_gz.name
        try:
            tmp_out = target.with_suffix(".mmdb.tmp")
            with gzip.open(gz_path, "rb") as src, open(tmp_out, "wb") as dst:
                shutil.copyfileobj(src, dst)
            tmp_out.replace(target)
        finally:
            os.unlink(gz_path)


def _candidate_year_months() -> Iterator[str]:
    now = datetime.now(UTC)
    yield f"{now.year:04d}-{now.month:02d}"
    prev_year, prev_month = (now.year - 1, 12) if now.month == 1 else (now.year, now.month - 1)
    yield f"{prev_year:04d}-{prev_month:02d}"
