#!/usr/bin/env python3
import subprocess
import sys

from feeds import FEEDS
from fetch import fetch_and_pool
from render import render
from resolve import resolve_links
from summarize import summarize


def main() -> None:
    print("Fetching feeds...")
    items = fetch_and_pool(FEEDS)
    if not items:
        print("No items fetched — check your network or feed URLs.")
        sys.exit(1)
    print(f"  {len(items)} items from the last 24 hours")

    print("Summarizing...")
    try:
        raw_markdown = summarize(items)
    except Exception as exc:
        print(f"  [error] Summarization failed: {exc}")
        print("  Falling back to raw item list...")
        raw_markdown = _fallback_markdown(items)

    resolved = resolve_links(raw_markdown, items)
    path = render(resolved)
    print(f"Done — {path.resolve()}")

    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)


def _fallback_markdown(items) -> str:
    lines = ["## Today's Articles\n"]
    by_source: dict[str, list] = {}
    for item in items:
        by_source.setdefault(item.source, []).append(item)
    for source, source_items in by_source.items():
        lines.append(f"### {source}\n")
        for item in source_items:
            lines.append(f"- [{item.title}]({item.link})")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
