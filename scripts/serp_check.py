#!/usr/bin/env python3
"""Decide whether a fetched search-engine result page actually contains results.

A page counts as valid only when at least MIN_LINKS result links can be extracted.
Captcha pages, JavaScript redirect shells and empty pages are reported with a reason,
so "HTTP 200 and non-empty body" is never mistaken for a successful search.

Standard library only. Usage:
    python3 scripts/serp_check.py page.html <engine> [--json-out check.json]
Exit code 0 = valid, 1 = invalid.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

MIN_LINKS = 3

BLOCK_MARKERS = [
    "captcha", "unusual traffic", "are you a robot", "not a robot", "verify you are human",
    "please enable javascript", "enable javascript to continue", "javascript is required",
    "if you are not redirected", "please click here if you are not redirected", "too many requests",
    "百度安全验证", "安全验证", "验证码", "人机验证", "访问异常", "访问过于频繁", "antispider",
    "没有被重定向", "正在重定向", "请开启javascript", "请启用javascript",
]

ENGINE_DOMAINS = [
    "bing.com", "bing.net", "microsoft.com", "msn.com", "baidu.com", "bdstatic.com", "bdimg.com",
    "sogou.com", "sogoucdn.com", "so.com", "360.cn", "qhimg.com", "qhres.com", "google.", "gstatic.com",
    "googleusercontent.com", "youtube.com/redirect", "duckduckgo.com", "qwant.com", "brave.com",
    "yahoo.com", "yimg.com", "startpage.com", "ecosia.org", "wolframalpha.com", "toutiaostatic.com",
    "bytedance.com", "byteimg.com", "pstatp.com", "w3.org", "schema.org", "beian.miit.gov.cn",
]
SAME_SITE_CONTENT = {
    # engine: path prefixes on its own domain that are real content, not navigation
    "toutiao": ["/article/", "/group/", "/a", "/w/", "/video/"],
}
STATIC_SUFFIXES = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2", ".json", ".xml")
WRAPPER_PATTERNS = [
    ("baidu.com", "/link"), ("sogou.com", "/link"), ("so.com", "/link"), ("toutiao.com", "/search/jump"),
]


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self.mu_urls: list[str] = []
        self._stack: list[dict] = []
        self.text_parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        attr = {k: (v or "") for k, v in attrs}
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        for key in ("mu", "data-mdurl", "data-url"):
            value = attr.get(key, "")
            if value.startswith("http"):
                self.mu_urls.append(value)
        if tag == "a":
            self._stack.append({"href": attr.get("href", ""), "alt": attr.get("data-mdurl", "") or attr.get("data-url", ""), "text": []})

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag == "a" and self._stack:
            item = self._stack.pop()
            item["text"] = " ".join(" ".join(item["text"]).split())
            self.links.append(item)

    def handle_data(self, data):
        if self._skip:
            return
        self.text_parts.append(data)
        if self._stack:
            self._stack[-1]["text"].append(data)


def _decode_bing(url: str) -> str:
    query = parse_qs(urlsplit(url).query)
    value = (query.get("u") or [""])[0]
    if value.startswith("a1"):
        raw = value[2:]
        raw += "=" * (-len(raw) % 4)
        try:
            return base64.urlsafe_b64decode(raw).decode("utf-8", "ignore")
        except Exception:
            return ""
    return ""


def resolve_href(href: str, base: str) -> tuple[str, bool]:
    """Return (url, is_wrapper). Unwrap known redirectors; wrappers whose target is hidden keep is_wrapper=True."""
    href = (href or "").strip()
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
        return "", False
    url = urljoin(base, href)
    parts = urlsplit(url)
    host = parts.netloc.lower()
    query = parse_qs(parts.query)
    if "google." in host and parts.path == "/url":
        return (query.get("q") or query.get("url") or [""])[0], False
    if "duckduckgo.com" in host and "uddg" in query:
        return unquote(query["uddg"][0]), False
    if "bing.com" in host and parts.path.startswith("/ck/"):
        return _decode_bing(url), False
    if "toutiao.com" in host and parts.path.startswith("/search/jump") and "url" in query:
        return unquote(query["url"][0]), False
    for domain, prefix in WRAPPER_PATTERNS:
        if domain in host and parts.path.startswith(prefix):
            return url, True
    return url, False


def _is_engine_url(url: str, engine: str) -> bool:
    """True for the engine's own navigation, ads, static hosts and other non-result links."""
    parts = urlsplit(url)
    host = parts.netloc.lower()
    own_content = SAME_SITE_CONTENT.get(engine)
    if own_content and engine in host:
        return not any(parts.path.startswith(prefix) for prefix in own_content)
    target = host + parts.path
    return any(domain in target for domain in ENGINE_DOMAINS)


def domain_of(url: str) -> str:
    host = urlsplit(url).netloc.lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def assess(html: str, engine: str = "", base_url: str = "https://example.invalid/") -> dict:
    parser = _LinkParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        pass
    text = " ".join(" ".join(parser.text_parts).split()).lower()
    marker = next((m for m in BLOCK_MARKERS if m in text), None)

    seen: set[str] = set()
    links: list[dict] = []
    wrappers = 0
    candidates = [(item["alt"] or item["href"], item["text"]) for item in parser.links]
    candidates += [(url, "") for url in parser.mu_urls]
    for href, title in candidates:
        url, is_wrapper = resolve_href(href, base_url)
        if not url or not url.startswith("http"):
            continue
        path = urlsplit(url).path.lower()
        if path.endswith(STATIC_SUFFIXES):
            continue
        if is_wrapper:
            if len(title) >= 4 and url not in seen:
                seen.add(url)
                wrappers += 1
                links.append({"title": title[:200], "url": url, "domain": "", "wrapped": True})
            continue
        if _is_engine_url(url, engine):
            continue
        key = url.split("#")[0]
        if key in seen:
            continue
        seen.add(key)
        links.append({"title": title[:200], "url": key, "domain": domain_of(key), "wrapped": False})

    titled = [link for link in links if len(link["title"]) >= 4 or not link["wrapped"]]
    count = len(titled)
    domains = sorted({link["domain"] for link in titled if link["domain"]})
    if count >= MIN_LINKS:
        valid, reason = True, "ok" if not marker else "ok (page also mentions: %s)" % marker
    elif marker:
        valid, reason = False, "blocked or redirect page: %s" % marker
    elif len(html) < 3000:
        valid, reason = False, "page too small to contain results"
    else:
        valid, reason = False, "fewer than %d result links (page structure changed, JS-only page, or no results)" % MIN_LINKS
    return {
        "engine": engine,
        "valid": valid,
        "reason": reason,
        "bytes": len(html.encode("utf-8", "ignore")),
        "result_links": count,
        "wrapped_links": wrappers,
        "domains": domains,
        "links": titled[:20],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html_file")
    ap.add_argument("engine", nargs="?", default="")
    ap.add_argument("--base-url", default="https://example.invalid/")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    raw = Path(args.html_file).read_bytes()
    for encoding in ("utf-8", "gb18030"):
        try:
            html = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        html = raw.decode("utf-8", "ignore")
    result = assess(html, args.engine, args.base_url)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
