import re

from fetch import Item

# Matches [n] or [n, m, ...] citation markers but not Markdown links like [text](url)
_CITATION_RE = re.compile(r'\[(\d+(?:,\s*\d+)*)\](?!\()')


def resolve_links(markdown: str, items: list[Item]) -> str:
    """Replace [n] and [n, m, ...] citation markers with Markdown hyperlinks.

    Unknown IDs are dropped silently rather than left as broken markers.
    """
    id_to_item = {item.id: item for item in items}

    def replace(match: re.Match) -> str:
        ids = [int(s.strip()) for s in match.group(1).split(",")]
        links = []
        for item_id in ids:
            item = id_to_item.get(item_id)
            if item is not None:
                links.append(f"[[{item_id}]]({item.link})")
        return " ".join(links)

    return _CITATION_RE.sub(replace, markdown)
