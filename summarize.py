import os
import time
import random

from google import genai
from google.genai import types as genai_types

from fetch import Item

# Update this constant if Google releases a newer free-tier Flash model.
# Verify current model names at: https://aistudio.google.com/
MODEL = "gemini-2.5-flash"

_SYSTEM_PROMPT = """\
You are writing a personal morning news rundown. The reader wants to stay informed on \
international affairs and notable tech news. Keep it tight and scannable — short sections \
or paragraphs, not a wall of text. Group related stories across sources where they overlap.

Per-source curation rules:
- World (NYT) and Politics (NYT): Focus on foreign policy and international affairs. \
Skip culture, human-interest, lifestyle, sports, and domestic-only stories that have no \
meaningful foreign-policy angle.
- TechCrunch: Cover notable tech news broadly; no narrow filter.

Cite every article you reference with its integer ID in square brackets, e.g. [1] or [3]. \
Use only the IDs provided in the article list below — do not invent IDs. \
Articles you choose to skip simply do not appear in the summary. \
Do NOT include any URLs in your response; IDs are the only citation mechanism."""

_RETRY_DELAYS = [1, 2, 4]  # seconds before each retry; give up after the last one


def _build_item_list(items: list[Item]) -> str:
    lines = []
    for item in items:
        blurb = item.blurb
        if len(blurb) > 400:
            blurb = blurb[:400] + "..."
        line = f"[{item.id}] ({item.source}) {item.title}"
        if blurb:
            line += f" — {blurb}"
        line += " — (link withheld; reference by ID)"
        lines.append(line)
    return "\n".join(lines)


def _is_rate_limit(exc: Exception) -> bool:
    exc_str = str(exc).lower()
    return "429" in str(exc) or "resource_exhausted" in exc_str or "quota" in exc_str


def summarize(items: list[Item]) -> str:
    """Call Gemini API with pooled items and return Markdown containing [n] citations.

    All provider-specific code lives here. The rest of the pipeline only knows
    that items go in and Markdown with [n] markers comes out.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Get a free key at https://aistudio.google.com/ and export it."
        )

    client = genai.Client(api_key=api_key)
    user_prompt = f"Here are today's articles:\n\n{_build_item_list(items)}"

    last_exc: Exception | None = None
    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                ),
            )
            return response.text
        except Exception as exc:
            last_exc = exc
            if not _is_rate_limit(exc) or attempt >= len(_RETRY_DELAYS):
                break
            wait = _RETRY_DELAYS[attempt] + random.uniform(0, 0.5)
            print(f"  [warn] Gemini rate limit hit, retrying in {wait:.1f}s… (attempt {attempt + 1})")
            time.sleep(wait)

    raise RuntimeError(f"Gemini API call failed after retries: {last_exc}") from last_exc
