"""
SHADE Visual Design System.

Two explicit palettes — LIGHT_THEME and DARK_THEME — are the only place
hex colours are defined. Injected CSS, Streamlit chrome, matplotlib
diagrams, and Graphviz nodes all read from get_palette().

Public API
----------
apply_theme()   Call once in app.py after init_state().
get_palette()   Active LIGHT_THEME / DARK_THEME dict.
"""

from __future__ import annotations

import streamlit as st

# ═══════════════════════════════════════════════════════════════════════════
#  Palettes — the only hardcoded hex colours in the app
# ═══════════════════════════════════════════════════════════════════════════

LIGHT_THEME: dict = {
    "bg": "#F4F7FA",
    "bg_secondary": "#FFFFFF",
    "text_primary": "#152028",
    "text_secondary": "#3A4C58",
    "border": "#23272A",
    "code_bg": "#E8EEF3",
    "code_text": "#152028",
    "accent": "#0A6B65",
}

DARK_THEME: dict = {
    "bg": "#0B1117",
    "bg_secondary": "#151E28",
    "text_primary": "#F3F7F8",
    "text_secondary": "#B4C2CC",
    "border": "#3A4D5C",
    "code_bg": "#0D1520",
    "code_text": "#E6EEF2",
    "accent": "#2EC9B6",
}


# ═══════════════════════════════════════════════════════════════════════════
#  Colour helpers (derive CSS from the 8 palette keys — no extra hex)
# ═══════════════════════════════════════════════════════════════════════════

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"


def _luminance(hex_color: str) -> float:
    def _lin(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contrast_ratio(a: str, b: str) -> float:
    l1, l2 = _luminance(a), _luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _on_color(fill: str, light: str, dark: str) -> str:
    """Pick whichever of `light` / `dark` contrasts better against `fill`."""
    return light if _contrast_ratio(fill, light) >= _contrast_ratio(fill, dark) else dark


def _adjust(hex_color: str, factor: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return _rgb_to_hex(int(r * factor), int(g * factor), int(b * factor))


def get_palette() -> dict:
    """Return the active 8-key palette for the current theme."""
    return DARK_THEME if st.session_state.get("shade_dark_mode", True) else LIGHT_THEME


def contrasting_text(fill: str) -> str:
    """Pick text_primary or bg, whichever reads better on `fill`."""
    p = get_palette()
    return _on_color(fill, p["text_primary"], p["bg"])


def apply_theme() -> None:
    """Inject theme CSS. Call once in app.py."""
    if "shade_dark_mode" not in st.session_state:
        st.session_state.shade_dark_mode = True

    # Light mode has a known tooltip-contrast bug (Streamlit's baseweb
    # tooltips render dark-on-dark against the light palette). Toggle
    # hidden until that's fixed with real DOM access -- see design.md.
    # st.toggle(
    #     "Dark mode",
    #     key="shade_dark_mode",
    #     help="Switch between dark and light appearance",
    # )

    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:'
        'wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    inject_theme_css()


def inject_theme_css() -> None:
    """Re-inject palette CSS last so it wins over Streamlit's own theme sheet."""
    st.markdown(f"<style>{_build_css(get_palette())}</style>", unsafe_allow_html=True)


def _build_css(p: dict) -> str:
    is_light = _luminance(p["bg"]) > 0.5
    color_scheme = "light" if is_light else "dark"
    accent_hover = _adjust(p["accent"], 0.88)
    on_accent = _on_color(p["accent"], p["text_primary"], p["bg"])
    on_secondary = _on_color(p["bg_secondary"], p["text_primary"], p["bg"])
    glass_bg = _rgba(p["bg_secondary"], 0.96)
    glass_border = _rgba(p["border"], 0.95)
    shadow = _rgba(p["text_primary"], 0.08 if is_light else 0.35)
    shadow_lg = _rgba(p["text_primary"], 0.14 if is_light else 0.50)
    accent_glow = _rgba(p["accent"], 0.22)
    bg_gradient = f"linear-gradient(170deg, {p['bg']} 0%, {p['bg_secondary']} 100%)"

    return f"""
:root {{
    --shade-bg:              {p["bg"]};
    --shade-bg-secondary:    {p["bg_secondary"]};
    --shade-text-primary:    {p["text_primary"]};
    --shade-text-secondary:  {p["text_secondary"]};
    --shade-border:          {p["border"]};
    --shade-code-bg:         {p["code_bg"]};
    --shade-code-text:       {p["code_text"]};
    --shade-accent:          {p["accent"]};
    --shade-accent-hover:    {accent_hover};
    --shade-on-accent:       {on_accent};
    --shade-radius:          12px;
    --shade-radius-sm:       8px;
    --shade-font:            'Inter', -apple-system, BlinkMacSystemFont,
                             'Segoe UI', Roboto, sans-serif;
    --background-color: {p["bg"]};
    --secondary-background-color: {p["bg_secondary"]};
    --text-color: {p["text_primary"]};
    --primary-color: {p["accent"]};
}}

html, body, .stApp {{
    color-scheme: {color_scheme} !important;
    background-color: var(--shade-bg) !important;
    background-image: {bg_gradient} !important;
    color: var(--shade-text-primary) !important;
    font-family: var(--shade-font) !important;
}}

[data-baseweb="tooltip"],
[role="tooltip"] {{
    background-color: #1a1a1a !important;
    color: #ffffff !important;
}}
[data-baseweb="tooltip"] *,
[role="tooltip"] * {{
    color: #ffffff !important;
}}

[data-testid="stHeader"],
[data-testid="stBottom"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
.block-container,
section.main {{
    background-color: var(--shade-bg) !important;
    color: var(--shade-text-primary) !important;
}}

[data-testid="stSidebar"] {{
    background-color: var(--shade-bg-secondary) !important;
    border-right: 1px solid var(--shade-border) !important;
    color: var(--shade-text-primary) !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small {{
    color: var(--shade-text-primary) !important;
}}

[data-testid="stSidebar"] [data-testid="stButton"] button,
[data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stMarkdownContainer"] span {{
    color: var(--shade-on-accent) !important;
}}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: var(--shade-text-secondary) !important;
}}

[data-testid="stSidebar"] h2 {{
    color: var(--shade-accent) !important;
    font-family: var(--shade-font) !important;
    font-weight: 700 !important;
}}

[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {{
    color: var(--shade-text-primary) !important;
    font-family: var(--shade-font) !important;
}}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
    font-family: var(--shade-font) !important;
    color: var(--shade-text-primary) !important;
}}

.stApp h1 {{ font-weight: 800 !important; letter-spacing: -0.03em !important; }}
.stApp h2, .stApp h3 {{ font-weight: 700 !important; }}
.stApp h4 {{ font-weight: 600 !important; }}

.stApp p, .stApp li, .stApp span, .stApp label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {{
    color: var(--shade-text-primary) !important;
}}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {{
    color: var(--shade-text-secondary) !important;
}}

[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {glass_bg} !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid {glass_border} !important;
    border-radius: var(--shade-radius) !important;
    box-shadow: 0 1px 4px {shadow} !important;
    color: {on_secondary} !important;
}}

[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: var(--shade-accent) !important;
    box-shadow: 0 4px 16px {shadow_lg} !important;
}}

.stButton > button {{
    background-color: var(--shade-accent) !important;
    color: var(--shade-on-accent) !important;
    border: none !important;
    border-radius: var(--shade-radius-sm) !important;
    font-family: var(--shade-font) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}}

.stButton > button:hover {{
    background-color: var(--shade-accent-hover) !important;
    box-shadow: 0 4px 14px {accent_glow} !important;
    color: var(--shade-on-accent) !important;
}}

.stButton > button:disabled {{
    background-color: var(--shade-border) !important;
    color: var(--shade-text-secondary) !important;
    opacity: 0.85 !important;
    box-shadow: none !important;
}}

[data-testid="stMetricValue"] {{
    color: var(--shade-accent) !important;
    font-family: var(--shade-font) !important;
    font-weight: 700 !important;
}}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricDelta"] {{
    color: var(--shade-text-secondary) !important;
}}

[data-testid="stCode"],
[data-testid="stCode"] pre,
[data-testid="stCode"] code,
code, pre {{
    background-color: var(--shade-code-bg) !important;
    color: var(--shade-code-text) !important;
    border-color: var(--shade-border) !important;
    border-radius: var(--shade-radius-sm) !important;
}}

[data-testid="stJson"],
[data-testid="stJson"] * {{
    background-color: var(--shade-code-bg) !important;
    color: var(--shade-code-text) !important;
}}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] > div {{
    background-color: var(--shade-bg-secondary) !important;
    color: var(--shade-text-primary) !important;
    border: 1px solid var(--shade-border) !important;
    border-radius: var(--shade-radius-sm) !important;
    caret-color: var(--shade-text-primary) !important;
}}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {{
    border-color: var(--shade-accent) !important;
    box-shadow: 0 0 0 3px {accent_glow} !important;
}}

.stSlider [data-testid="stThumbValue"],
.stSlider label, .stSlider p {{
    color: var(--shade-text-primary) !important;
}}

.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: var(--shade-accent) !important;
}}

[data-testid="stAlert"] {{
    background-color: var(--shade-bg-secondary) !important;
    color: var(--shade-text-primary) !important;
    border: 1px solid var(--shade-accent) !important;
    border-radius: var(--shade-radius-sm) !important;
}}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {{
    color: var(--shade-text-primary) !important;
}}

[data-testid="stAlertContainer"],
[data-testid="stAlertContainer"] > div,
[data-testid="stNotification"] {{
    background-color: var(--shade-bg-secondary) !important;
    color: var(--shade-text-primary) !important;
    border-color: var(--shade-accent) !important;
}}

[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] span,
[data-testid="stAlertContentError"],
[data-testid="stAlertContentSuccess"],
[data-testid="stAlertContentInfo"],
[data-testid="stAlertContentWarning"] {{
    color: var(--shade-text-primary) !important;
    background-color: var(--shade-bg-secondary) !important;
}}

[data-testid="stExpander"] {{
    background-color: var(--shade-bg-secondary) !important;
    border: 1px solid var(--shade-border) !important;
    border-radius: var(--shade-radius) !important;
}}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {{
    color: var(--shade-text-primary) !important;
}}

hr {{
    border-color: var(--shade-border) !important;
    opacity: 0.8;
}}

::-webkit-scrollbar {{ width: 7px; height: 7px; }}
::-webkit-scrollbar-track {{ background: var(--shade-bg); }}
::-webkit-scrollbar-thumb {{
    background: var(--shade-border);
    border-radius: 4px;
}}

[data-testid="stVegaLiteChart"],
[data-testid="stGraphVizChart"] {{
    background-color: var(--shade-bg-secondary) !important;
    border-radius: var(--shade-radius-sm);
    padding: 6px;
}}

[data-testid="stImage"] {{
    border-radius: var(--shade-radius-sm);
    overflow: hidden;
}}

/* Toggle switch + its label (sidebar Dark mode / Guided mode).
   Streamlit 1.63 renders st.toggle as data-testid="stCheckbox". */
[data-testid="stToggle"] p,
[data-testid="stToggle"] span,
[data-testid="stToggle"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span,
[data-testid="stCheckbox"] label {{
    color: var(--shade-text-primary) !important;
}}

[data-testid="stToggle"] [role="checkbox"],
[data-testid="stToggle"] [role="switch"],
[data-testid="stCheckbox"] [role="checkbox"],
[data-testid="stCheckbox"] [role="switch"],
[data-baseweb="switch"],
[data-baseweb="checkbox"] {{
    background-color: var(--shade-border) !important;
}}

[data-testid="stToggle"] [role="checkbox"][aria-checked="true"],
[data-testid="stToggle"] [role="switch"][aria-checked="true"],
[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"],
[data-testid="stCheckbox"] [role="switch"][aria-checked="true"],
[data-baseweb="switch"][aria-checked="true"],
[data-baseweb="checkbox"][aria-checked="true"] {{
    background-color: var(--shade-accent) !important;
}}

.stMarkdown, .stCaption, .stText, .stAlert {{
    color: var(--shade-text-primary) !important;
}}

.stCodeBlock, .stCode, [data-testid="stCodeBlock"] {{
    background-color: var(--shade-code-bg) !important;
    color: var(--shade-code-text) !important;
}}

.stRadio label, .stRadio p,
[data-testid="stRadio"] p,
[data-testid="stRadio"] span {{
    color: var(--shade-text-primary) !important;
}}

[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploaderDropzone"] {{
    color: var(--shade-text-primary) !important;
    background-color: var(--shade-bg-secondary) !important;
    border-color: var(--shade-border) !important;
}}

footer {{ visibility: hidden !important; }}

/* Button labels are <p>/<span> inside the control — beat the global text rule. */
div[data-testid="stButton"] button {{
    background-color: var(--shade-accent) !important;
    color: var(--shade-on-accent) !important;
}}
div[data-testid="stButton"] button p,
div[data-testid="stButton"] button span,
div[data-testid="stButton"] [data-testid="stMarkdownContainer"] p {{
    color: var(--shade-on-accent) !important;
    background-color: transparent !important;
}}

.stButton > button:disabled,
.stButton > button:disabled * {{
    color: var(--shade-text-secondary) !important;
}}

/* Issue 1 -- reduce Streamlit's large default top/bottom page padding so
   primary action buttons (Run Full Pipeline / Show Results Summary) are
   visible without scrolling on a standard viewport. */
[data-testid="stMainBlockContainer"],
.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}}

/* Copy-to-clipboard icon on st.code() blocks. Streamlit 1.63 renders this
   inside a hover "element toolbar", not a plain <button svg>, so the earlier
   selector guess didn't match. Targeting the toolbar wrapper broadly here --
   if this still doesn't fully fix it, the real fix needs the exact DOM from
   browser devtools (right-click the icon -> Inspect). */
[data-testid="stElementToolbar"],
[data-testid="stElementToolbar"] button {{
    background-color: var(--shade-code-bg) !important;
    border: 1px solid var(--shade-border) !important;
    border-radius: var(--shade-radius-sm) !important;
}}
[data-testid="stElementToolbar"] svg,
[data-testid="stElementToolbarButton"] svg,
[data-testid="stCodeCopyButton"] svg,
[data-testid="stCode"] button svg,
button[title="Copy to clipboard"] svg {{
    fill: var(--shade-code-text) !important;
    color: var(--shade-code-text) !important;
}}
[data-testid="stElementToolbarButton"] {{
    background-color: transparent !important;
}}
[data-testid="stElementToolbarButton"]:hover {{
    background-color: var(--shade-border) !important;
}}

/* Issue 3 -- dashboard card tiles get a gentle min-height floor only.
   Deliberately NO display:flex / justify-content / hard height here --
   that combination previously made Streamlit's column layout stretch
   cards to hundreds of pixels tall. A plain min-height can't trigger
   that: content shorter than the floor just leaves quiet whitespace
   below it instead of exploding. */
div[class*="st-key-dashboard_card_"] {{
    min-height: 200px !important;
}}
"""