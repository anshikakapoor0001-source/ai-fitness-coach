import html
import re

import bleach
import markdown
from markupsafe import Markup


ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
}
ALLOWED_ATTRIBUTES = {"a": ["href", "title", "rel", "target"]}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


LABEL_HEADINGS = {
    "breakfast",
    "mid-morning snack",
    "lunch",
    "evening snack",
    "dinner",
    "water intake",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


def normalize_markdown(value):
    text = html.unescape(str(value or "")).strip()
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"^(#{1,6})([^#\s])", r"\1 \2", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[•*]\s+", "- ", text, flags=re.MULTILINE)

    lines = []
    for line in text.split("\n"):
        label, separator, rest = line.partition(":")
        normalized_label = label.strip().lower()
        if separator and normalized_label in LABEL_HEADINGS:
            heading = label.strip().title()
            lines.extend([f"### {heading}", ""])
            if rest.strip():
                lines.append(f"- {rest.strip()}")
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def render_markdown(value):
    """Render generated Markdown safely for templates."""
    text = normalize_markdown(value)
    html = markdown.markdown(
        text,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return Markup(cleaned)
