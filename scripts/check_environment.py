#!/usr/bin/env python3
"""Validate the local environment before running the ServiceNow smoke test."""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _check_import(name: str) -> CheckResult:
    try:
        importlib.import_module(name)
        return CheckResult(name, True, "installed")
    except Exception as exc:
        return CheckResult(name, False, f"missing ({exc})")


def _check_python_version() -> CheckResult:
    ok = sys.version_info >= (3, 11) and sys.version_info < (3, 14)
    return CheckResult(
        "python",
        ok,
        f"{sys.version.split()[0]} ({sys.executable})",
    )


def _check_env(name: str, *, required: bool = True) -> CheckResult:
    value = os.getenv(name, "").strip()
    if value:
        return CheckResult(name, True, "set")
    if required:
        return CheckResult(name, False, "missing")
    return CheckResult(name, True, "unset")


def _check_instance_url() -> CheckResult:
    value = os.getenv("SERVICENOW_INSTANCE_URL", "").strip()
    if not value:
        return CheckResult("SERVICENOW_INSTANCE_URL", False, "missing")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return CheckResult("SERVICENOW_INSTANCE_URL", False, f"invalid URL: {value}")
    return CheckResult("SERVICENOW_INSTANCE_URL", True, f"valid ({value})")


def main() -> int:
    checks = [
        _check_python_version(),
        _check_import("requests"),
        _check_import("httpx"),
        _check_import("yaml"),
        _check_import("dotenv"),
        _check_instance_url(),
        _check_env("SERVICENOW_USERNAME"),
        _check_env("SERVICENOW_PASSWORD"),
    ]

    print("Hermes ServiceNow Environment Check")
    print("-----------------------------------")
    for result in checks:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status:<4} {result.name}: {result.detail}")

    failures = [result for result in checks if not result.ok]
    if failures:
        print()
        print("Overall: FAIL")
        return 1

    print()
    print("Overall: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
