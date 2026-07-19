#!/usr/bin/env python3
"""Compare cached and cache-bypass delivery reliability on Hostinger CDN."""
from __future__ import annotations

import concurrent.futures
import json
import ssl
import statistics
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "scripts" / "cdn_delivery_report.json"
BASE = "https://abralion.com"
ASSETS = (
    "/",
    "/assets/css/bundle.min.css",
    "/assets/js/home.bundle.min.js",
    "/assets/images/home/hero-bg-480.avif",
    "/assets/fonts/inter-tr-400-normal.woff2",
)


def request_asset(path: str, bypass: bool) -> dict:
    suffix = f"?perf_audit={uuid.uuid4().hex}" if bypass and "?" not in path else ""
    url = f"{BASE}{path}{suffix}"
    headers = {
        "User-Agent": "Abralion-Delivery-Audit/1.0",
        "Cache-Control": "no-cache" if bypass else "max-age=0",
    }
    request = urllib.request.Request(url, headers=headers)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=15, context=context) as response:
            response.read()
            return {
                "path": path,
                "status": response.status,
                "elapsed_ms": round((time.perf_counter() - started) * 1000),
                "cache": response.headers.get("x-hcdn-cache-status", ""),
                "edge": response.headers.get("x-hcdn-request-id", ""),
                "age": response.headers.get("Age", ""),
            }
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "path": path,
            "status": 0,
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "cache": "",
            "edge": "",
            "age": "",
            "error": str(error),
        }


def run_mode(name: str, bypass: bool) -> dict:
    requests = list(ASSETS) * 3
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda path: request_asset(path, bypass), requests))
    successful = [item["elapsed_ms"] for item in results if item["status"] == 200]
    return {
        "mode": name,
        "requests": len(results),
        "failures": sum(item["status"] != 200 for item in results),
        "median_ms": round(statistics.median(successful)) if successful else None,
        "p95_ms": round(sorted(successful)[max(0, round(len(successful) * 0.95) - 1)])
        if successful
        else None,
        "cache_statuses": {
            status: sum(item["cache"] == status for item in results)
            for status in sorted({item["cache"] for item in results})
        },
        "results": results,
    }


def main() -> int:
    report = {
        "base_url": BASE,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modes": [
            run_mode("cdn-cache", bypass=False),
            run_mode("cache-bypass", bypass=True),
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    for mode in report["modes"]:
        print(
            f"{mode['mode']}: failures={mode['failures']}/{mode['requests']} "
            f"median={mode['median_ms']}ms p95={mode['p95_ms']}ms "
            f"cache={mode['cache_statuses']}"
        )
    return 1 if any(mode["failures"] for mode in report["modes"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
