#!/usr/bin/env python3
"""Measure which keyless search engines return real result pages in the current network.

Fetches each engine once per query, validates the page with serp_check.assess and prints a table.
Standard library only; no files are written unless --json-out is given.

    python3 scripts/probe-search.py
    python3 scripts/probe-search.py --query "新能源车 出口 欧洲 关税" --timeout 15
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("serp_check", HERE / "serp_check.py")
serp_check = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(serp_check)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# The 17 engines listed in skills/multi-search-engine/SKILL.md, plus DuckDuckGo Lite.
ENGINES = [
    ("baidu", "https://www.baidu.com/s?wd={q}"),
    ("bing_cn", "https://cn.bing.com/search?q={q}&ensearch=0"),
    ("bing_int", "https://cn.bing.com/search?q={q}&ensearch=1"),
    ("so360", "https://www.so.com/s?q={q}"),
    ("sogou", "https://sogou.com/web?query={q}"),
    ("wechat", "https://wx.sogou.com/weixin?type=2&query={q}"),
    ("toutiao", "https://so.toutiao.com/search?keyword={q}"),
    ("jisilu", "https://www.jisilu.cn/explore/?keyword={q}"),
    ("google", "https://www.google.com/search?q={q}"),
    ("google_hk", "https://www.google.com.hk/search?q={q}"),
    ("duckduckgo", "https://duckduckgo.com/html/?q={q}"),
    ("ddg_lite", "https://lite.duckduckgo.com/lite/?q={q}"),
    ("yahoo", "https://search.yahoo.com/search?p={q}"),
    ("startpage", "https://www.startpage.com/sp/search?query={q}"),
    ("brave", "https://search.brave.com/search?q={q}"),
    ("ecosia", "https://www.ecosia.org/search?q={q}"),
    ("qwant", "https://www.qwant.com/?q={q}&t=web"),
    ("wolframalpha", "https://www.wolframalpha.com/input?i={q}"),
]


def fetch(url: str, timeout: float) -> tuple[int, bytes, str, float]:
    started = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            return response.status, body, response.geturl(), time.monotonic() - started
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read() or b"", url, time.monotonic() - started
    except Exception as exc:  # network error, timeout, TLS
        return 0, str(exc).encode(), url, time.monotonic() - started


def decode(body: bytes) -> str:
    for encoding in ("utf-8", "gb18030"):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", "ignore")


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe keyless search engines")
    ap.add_argument("--query", action="append", help="Query to test (repeatable). Default: an English and a Chinese query.")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--json-out")
    args = ap.parse_args()
    queries = args.query or ["deep research agent", "新能源车 出口 欧洲 关税"]

    rows = []
    for query in queries:
        print(f"\n查询: {query}")
        print(f"{'engine':<13}{'HTTP':>5}{'bytes':>10}{'sec':>6}  {'links':>5}  result")
        for name, template in ENGINES:
            url = template.format(q=urllib.parse.quote_plus(query))
            status, body, final_url, seconds = fetch(url, args.timeout)
            if status == 200 and body:
                check = serp_check.assess(decode(body), name, final_url)
            else:
                check = {"valid": False, "reason": f"HTTP {status}" if status else decode(body)[:80], "result_links": 0, "domains": []}
            mark = "✅" if check["valid"] else "❌"
            print(f"{name:<13}{status:>5}{len(body):>10}{seconds:>6.1f}  {check['result_links']:>5}  {mark} {check['reason']}")
            rows.append({"query": query, "engine": name, "http": status, "bytes": len(body), "seconds": round(seconds, 2),
                         "valid": check["valid"], "reason": check["reason"], "result_links": check["result_links"], "domains": check.get("domains", [])[:10]})
            time.sleep(1)
        ok = [r["engine"] for r in rows if r["query"] == query and r["valid"]]
        print(f"可用: {len(ok)}/{len(ENGINES)} → {', '.join(ok) or '无'}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n说明：结果受当前网络和代理影响（例如 fake-IP 模式的代理）。宿主自带的联网搜索通常比这些直连引擎可靠。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
