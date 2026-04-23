#!/usr/bin/env python
import atexit
import os
import signal
import subprocess
import sys
from pathlib import Path

from django.utils.autoreload import run_with_reloader


PROJECT_DIR = Path(__file__).resolve().parent
child_process: subprocess.Popen[str] | None = None


def stop_child() -> None:
    global child_process

    if child_process is None or child_process.poll() is not None:
        return

    child_process.terminate()
    try:
        child_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child_process.kill()
        child_process.wait(timeout=5)
    finally:
        child_process = None


def forward_exit(signum, _frame) -> None:
    stop_child()
    raise SystemExit(128 + signum)


def run_command() -> None:
    global child_process

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python dev_autoreload.py <command> [args...]")

    child_process = subprocess.Popen(sys.argv[1:], cwd=PROJECT_DIR)
    exit_code = child_process.wait()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    atexit.register(stop_child)
    signal.signal(signal.SIGINT, forward_exit)
    signal.signal(signal.SIGTERM, forward_exit)
    run_with_reloader(run_command)
