# Morning Brew

A personal morning news rundown. Pulls from hand-picked RSS feeds, runs the day's headlines through Gemini, and produces a tight scannable summary with inline article links. Runs every morning via GitHub Actions and publishes to GitHub Pages.

**[Read today's rundown →](https://iankim0.github.io/morning-brew/)**

---

## How it works

Six stages, one LLM call:

1. **Fetch** — pull and parse RSS feeds into structured items
2. **Normalize** — collapse all items into a common shape, tag by source
3. **Filter** — keep only the last 24 hours, assign stable IDs
4. **Summarize** — one Gemini call over the pooled list; model cites articles as `[n]`
5. **Resolve** — replace each `[n]` in the output with a real link from the fetched data (the LLM never sees URLs)
6. **Render** — convert Markdown to a self-contained HTML file

Feeds covered: NYT World, NYT Politics (foreign policy / international affairs), TechCrunch (broad tech).

## Running locally

**Prerequisites:** Python 3.11+, a free [Gemini API key](https://aistudio.google.com/)

```bash
git clone https://github.com/iankim0/morning-brew.git
cd morning-brew
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python rundown.py
```

Opens `public/index.html` in your browser when done.

## Scheduling

A GitHub Actions workflow (`.github/workflows/rundown.yml`) runs daily at 5:40 AM Eastern and deploys the result to GitHub Pages. The off-the-hour schedule avoids GitHub's peak-load delays, giving a ~20 min cushion for the page to be ready by 6 AM.

To run it manually: **Actions → Morning Rundown → Run workflow**.

## Adding a feed

Edit `feeds.py` — each entry is a `(source_tag, url)` tuple. The source tag controls curation behavior in the LLM prompt.

## Swapping the LLM

All provider-specific code is isolated in `summarize.py`. The rest of the pipeline only knows that a list of items goes in and Markdown with `[n]` citations comes out.
