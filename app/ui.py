"""Safe bidirectional Markdown rendering and shared web styles."""

import base64
import html
import re
from pathlib import Path

import bleach
from markdown import markdown


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "assets" / "fonts" / "Vazirmatn-Regular.ttf"
BLOCK_TAGS = r"p|h[1-6]|ul|ol|li|blockquote|pre|table|th|td"
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
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}


def page_css() -> str:
    """Return self-contained styles so the font also works on cloud deployments."""
    font = base64.b64encode(FONT_PATH.read_bytes()).decode() if FONT_PATH.exists() else ""
    return f"""
    <style>
    @font-face {{
        font-family: "Vazirmatn";
        src: url(data:font/ttf;base64,{font}) format("truetype");
        font-display: swap;
    }}
    :root {{
        --surface: #ffffff;
        --surface-muted: #f8fafc;
        --border: #e2e8f0;
        --ink: #172033;
        --muted: #64748b;
        --accent: #2563eb;
    }}
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background: linear-gradient(180deg, #f5f8ff 0, #ffffff 22rem);
        color: var(--ink);
        font-family: Inter, "Segoe UI", sans-serif;
    }}
    [data-testid="stHeader"] {{
        background: rgba(245, 248, 255, .92);
        color: var(--ink);
        backdrop-filter: blur(10px);
    }}
    [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        color: var(--ink);
    }}
    .block-container {{max-width: 1180px; padding-top: 2.5rem; padding-bottom: 4rem;}}
    .app-eyebrow {{
        color: var(--accent);
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .12em;
        margin-bottom: -.5rem;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, .94);
        border-color: var(--border);
        border-radius: 18px;
        box-shadow: 0 12px 35px rgba(15, 23, 42, .05);
    }}
    [data-testid="stMetric"] {{
        background: var(--surface-muted);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: .8rem 1rem;
    }}
    textarea, input, [data-testid="stDataFrame"] {{
        font-family: "Vazirmatn", Inter, "Segoe UI", sans-serif !important;
        unicode-bidi: plaintext;
    }}
    .analysis-output {{
        overflow-x: auto;
        background: var(--surface-muted);
        border: 1px solid var(--border);
        border-radius: 14px;
        margin: .5rem 0 1.25rem;
        padding: 1.25rem 1.4rem;
    }}
    .analysis-output [dir="auto"] {{
        unicode-bidi: plaintext;
        text-align: start;
    }}
    [data-testid="stExpander"] {{background: var(--surface); border-color: var(--border);}}
    [data-testid="stExpander"] p {{font-family: "Vazirmatn", Tahoma, sans-serif; unicode-bidi: plaintext;}}
    [data-testid="stExpander"] input {{direction: ltr; text-align: left;}}
    .st-key-llm_settings {{direction: rtl; font-family: "Vazirmatn", Tahoma, sans-serif;}}
    .st-key-llm_settings [data-testid="stExpander"] summary {{direction: rtl;}}
    .st-key-llm_settings p, .st-key-llm_settings label {{
        direction: rtl;
        text-align: right;
        unicode-bidi: normal;
        font-family: "Vazirmatn", Tahoma, sans-serif !important;
    }}
    .st-key-llm_settings button, .st-key-llm_settings input,
    .st-key-llm_settings [data-baseweb="select"] {{font-family: "Vazirmatn", Tahoma, sans-serif !important;}}
    .st-key-llm_settings [data-baseweb="select"] {{direction: rtl; text-align: right;}}
    .st-key-llm_settings input {{direction: ltr; text-align: right;}}
    [data-testid="stAlert"] p {{font-family: "Vazirmatn", Tahoma, sans-serif; unicode-bidi: plaintext;}}
    .analysis-output [dir="auto"]:dir(rtl) {{
        direction: rtl;
        font-family: "Vazirmatn", Tahoma, sans-serif;
        line-height: 2;
        text-align: right;
    }}
    .analysis-output [dir="auto"]:dir(ltr) {{
        direction: ltr;
        font-family: Inter, "Segoe UI", sans-serif;
        line-height: 1.7;
        text-align: left;
    }}
    .analysis-output table {{width: 100%; border-collapse: collapse; margin: 1rem 0;}}
    .analysis-output th, .analysis-output td {{border: 1px solid var(--border); padding: .65rem .8rem;}}
    .analysis-output th {{background: #eef4ff; font-weight: 700;}}
    .analysis-output pre, .analysis-output code {{
        direction: ltr !important;
        font-family: Consolas, monospace !important;
        text-align: left !important;
        unicode-bidi: isolate;
    }}
    .analysis-output h1, .analysis-output h2, .analysis-output h3 {{margin-top: 1.2rem;}}
    .analysis-output > :first-child {{margin-top: 0;}}
    .analysis-output > :last-child {{margin-bottom: 0;}}
    @media (max-width: 768px) {{
        .block-container {{padding: 1.5rem 1rem 3rem;}}
        [data-testid="stHorizontalBlock"] {{gap: .75rem;}}
        [data-testid="stMetric"] {{padding: .7rem .8rem;}}
    }}
    </style>
    """


def render_markdown(text: str) -> str:
    """Convert model Markdown to safe HTML with direction detection per block."""
    converted = markdown(html.escape(text), extensions=["fenced_code", "sane_lists", "tables"])
    cleaned = bleach.clean(
        converted,
        tags=ALLOWED_TAGS,
        attributes={"a": ["href", "title"], "code": ["class"]},
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    directed = re.sub(rf"<({BLOCK_TAGS})(?=[\s>])", r'<\1 dir="auto"', cleaned)
    return f'<section class="analysis-output">{directed}</section>'
