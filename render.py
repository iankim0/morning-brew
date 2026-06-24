from datetime import datetime
from pathlib import Path

import markdown as md_lib

OUTPUT_PATH = Path("public/index.html")

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 18px;
    line-height: 1.7;
    color: #1a1a1a;
    background: #fafaf8;
    padding: 2rem 1rem;
}
#wrap {
    max-width: 700px;
    margin: 0 auto;
}
header {
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 0.75rem;
    margin-bottom: 2rem;
}
header h1 {
    font-size: 1.5rem;
    font-weight: bold;
    letter-spacing: 0.02em;
}
header p {
    font-size: 0.9rem;
    color: #555;
    margin-top: 0.25rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
h2 {
    font-size: 1.15rem;
    font-weight: bold;
    margin-top: 2rem;
    margin-bottom: 0.5rem;
}
p { margin-top: 0.75rem; }
a {
    color: #1a4e8c;
    text-decoration: none;
}
a:hover { text-decoration: underline; }
ul, ol {
    margin-top: 0.75rem;
    padding-left: 1.5rem;
}
li { margin-top: 0.4rem; }
"""

_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Morning Brew — {date}</title>
<style>
{css}
</style>
</head>
<body>
<div id="wrap">
  <header>
    <h1>Morning Brew</h1>
    <p>{date}</p>
  </header>
  <main>
{body}
  </main>
</div>
</body>
</html>
"""


def render(resolved_markdown: str, output_path: Path = OUTPUT_PATH) -> Path:
    """Convert resolved Markdown to a self-contained HTML file."""
    body = md_lib.markdown(resolved_markdown, extensions=["extra"])
    date_str = datetime.now().strftime("%A, %B %-d, %Y")
    html = _TEMPLATE.format(date=date_str, css=_CSS, body=body)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
