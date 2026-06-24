import re
import feedparser
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser


@dataclass
class Item:
    id: int
    source: str
    title: str
    link: str
    published: datetime
    blurb: str


class _StripTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self):
        return " ".join(self._parts).strip()


def _strip_html(text: str) -> str:
    if not text:
        return ""
    p = _StripTags()
    p.feed(text)
    return re.sub(r"\s+", " ", p.get_text()).strip()


def _parse_published(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        import calendar
        ts = calendar.timegm(entry.published_parsed)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    return None


def fetch_feed(source: str, url: str) -> list[Item]:
    """Fetch one RSS feed and return unnormalized items (id=0 placeholder)."""
    feed = feedparser.parse(
        url,
        agent="MorningBrew/1.0 (personal news rundown; not a bot)",
    )
    if feed.bozo and not feed.entries:
        print(f"  [warn] {source}: feed parse error — {feed.bozo_exception}")
        return []

    items = []
    for entry in feed.entries:
        published = _parse_published(entry)
        if published is None:
            continue  # skip items with no parseable date

        title = (entry.get("title") or "").strip()
        link = entry.get("link") or entry.get("url") or ""
        blurb = _strip_html(entry.get("summary") or entry.get("description") or "")

        if not title or not link:
            continue

        items.append(Item(
            id=0,
            source=source,
            title=title,
            link=link,
            published=published,
            blurb=blurb,
        ))

    return items


def fetch_and_pool(feeds: list[tuple[str, str]], hours: int = 24) -> list[Item]:
    """
    Fetch all feeds, filter to the last `hours` hours, assign contiguous IDs,
    and return the pooled list sorted by published date (newest first).
    """
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    raw: list[Item] = []

    for source, url in feeds:
        try:
            items = fetch_feed(source, url)
            recent = [i for i in items if i.published >= cutoff]
            print(f"  {source}: {len(recent)}/{len(items)} items within {hours}h")
            raw.extend(recent)
        except Exception as exc:
            print(f"  [error] {source}: {exc}")

    raw.sort(key=lambda i: i.published, reverse=True)

    for idx, item in enumerate(raw, start=1):
        item.id = idx

    return raw


if __name__ == "__main__":
    from feeds import FEEDS

    print("Fetching feeds...")
    items = fetch_and_pool(FEEDS)
    print(f"\nTotal items: {len(items)}\n")
    for item in items:
        print(f"[{item.id}] ({item.source}) {item.published.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"  Title: {item.title}")
        print(f"  Link:  {item.link}")
        print(f"  Blurb: {item.blurb[:120]}{'...' if len(item.blurb) > 120 else ''}")
        print()
