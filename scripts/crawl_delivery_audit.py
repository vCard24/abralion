#!/usr/bin/env python3
"""Smoke-test public pages as search and AI crawlers."""
from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "scripts" / "crawl_delivery_report.json"
CRAWLERS = {
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (compatible; ClaudeBot/1.0; +https://anthropic.com)",
}
PATHS = ("/", "/urunler.html", "/urun/metal-inox-kesme-tasi.html")


def fetch(url: str, user_agent: str) -> dict:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=20, context=context) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "elapsed_ms": round((time.perf_counter() - started) * 1000),
                "bytes": len(body.encode("utf-8")),
                "body": body,
            }
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "status": 0,
            "content_type": "",
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "bytes": 0,
            "error": str(error),
            "body": "",
        }


def inspect_html(result: dict) -> list[str]:
    body = result.pop("body")
    issues = []
    if result["status"] != 200:
        issues.append(f"status={result['status']}")
        return issues
    if "text/html" not in result["content_type"]:
        issues.append(f"content-type={result['content_type']}")
    for label, pattern in (
        ("main", r"<main\b"),
        ("canonical", r'<link[^>]+rel=["\']canonical["\']'),
        ("description", r'<meta[^>]+name=["\']description["\']'),
        ("json-ld", r'application/ld\+json'),
    ):
        if not re.search(pattern, body, re.I):
            issues.append(f"{label} missing")
    if re.search(
        r"captcha|access denied|verify you are human|checking your browser|hcdn-cgi/jschallenge",
        body,
        re.I,
    ):
        issues.append("crawler challenge detected")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://abralion.com")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    checks = []
    issues = []

    for crawler, user_agent in CRAWLERS.items():
        for path in PATHS:
            result = fetch(f"{base}{path}", user_agent)
            item_issues = inspect_html(result)
            check = {"crawler": crawler, "path": path, **result, "issues": item_issues}
            checks.append(check)
            issues.extend(f"{crawler} {path}: {issue}" for issue in item_issues)

    for path, required in (
        ("/robots.txt", "User-agent: *"),
        ("/llms.txt", "## Ürün aileleri"),
        ("/sitemap.xml", "<urlset"),
    ):
        result = fetch(f"{base}{path}", CRAWLERS["Googlebot"])
        body = result.pop("body")
        item_issues = []
        if result["status"] != 200:
            item_issues.append(f"status={result['status']}")
        if required not in body:
            item_issues.append(f"missing marker: {required}")
        checks.append({"crawler": "Googlebot", "path": path, **result, "issues": item_issues})
        issues.extend(f"{path}: {issue}" for issue in item_issues)

    report = {"base_url": base, "checks": checks, "issues": issues}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}; checks={len(checks)} issues={len(issues)}")
    for issue in issues:
        print(f"  {issue}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
