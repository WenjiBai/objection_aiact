"""Visual theme controls for the Streamlit UI.

OBJECTION! AI ACT — modern legal-tech aesthetic with dark/light modes.
Public API preserved: init_theme_state, get_theme, set_theme, apply_theme,
render_theme_controls, export_theme_css, render_token_export, default_theme.
"""

from __future__ import annotations

import textwrap
from copy import deepcopy

import streamlit as st


THEME_STATE_KEY = "ui_theme_tokens"
MODE_STATE_KEY = "ui_theme_mode"


# ----------------------------------------------------------------- presets

# A theme dict carries semantic tokens plus a `mode` ("dark" | "light")
# and tier color tokens. Anything visual in the UI reads from these.

COURTROOM_NOIR = {
    "mode": "dark",
    "background": "#0A0B0F",
    "background_grain": "#0F1117",
    "surface": "#14161D",
    "surface_elevated": "#1B1E27",
    "surface_muted": "#10131A",
    "text": "#E8EAF0",
    "text_strong": "#FFFFFF",
    "muted_text": "#9298A8",
    "subtle_text": "#6B7280",
    "border": "#262934",
    "border_strong": "#353945",
    "primary": "#6366F1",
    "primary_strong": "#818CF8",
    "primary_soft": "rgba(99,102,241,0.18)",
    "primary_glow": "rgba(99,102,241,0.35)",
    "accent": "#F59E0B",
    "accent_soft": "rgba(245,158,11,0.15)",
    "danger": "#EF4444",
    "danger_soft": "rgba(239,68,68,0.14)",
    "warning": "#F59E0B",
    "warning_soft": "rgba(245,158,11,0.14)",
    "success": "#10B981",
    "success_soft": "rgba(16,185,129,0.14)",
    "info": "#38BDF8",
    "info_soft": "rgba(56,189,248,0.14)",
    "radius": 12,
    "density": 14,
    "hero_size": 32,
    "body_size": 14,
    "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    "mono": "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}

COURTROOM_DAYLIGHT = {
    "mode": "light",
    "background": "#F7F8FA",
    "background_grain": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface_elevated": "#FAFBFD",
    "surface_muted": "#F1F4F8",
    "text": "#0F172A",
    "text_strong": "#000000",
    "muted_text": "#475569",
    "subtle_text": "#94A3B8",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "primary": "#4F46E5",
    "primary_strong": "#4338CA",
    "primary_soft": "rgba(79,70,229,0.10)",
    "primary_glow": "rgba(79,70,229,0.22)",
    "accent": "#D97706",
    "accent_soft": "rgba(217,119,6,0.10)",
    "danger": "#DC2626",
    "danger_soft": "rgba(220,38,38,0.08)",
    "warning": "#D97706",
    "warning_soft": "rgba(217,119,6,0.10)",
    "success": "#059669",
    "success_soft": "rgba(5,150,105,0.10)",
    "info": "#0284C7",
    "info_soft": "rgba(2,132,199,0.10)",
    "radius": 12,
    "density": 14,
    "hero_size": 32,
    "body_size": 14,
    "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    "mono": "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}

# Legacy preset kept so prior selections still resolve.
FIGMA_COURTROOM = {
    "mode": "light",
    "background": "#fbfaf8",
    "background_grain": "#ffffff",
    "surface": "#ffffff",
    "surface_elevated": "#ffffff",
    "surface_muted": "#f5f4f1",
    "text": "#1c1b1f",
    "text_strong": "#0c0b10",
    "muted_text": "#605d66",
    "subtle_text": "#8a8790",
    "border": "#d8d5dd",
    "border_strong": "#c4c0cc",
    "primary": "#534AB7",
    "primary_strong": "#3F379A",
    "primary_soft": "rgba(83,74,183,0.10)",
    "primary_glow": "rgba(83,74,183,0.18)",
    "accent": "#BA7517",
    "accent_soft": "#EEEDFE",
    "danger": "#A32D2D",
    "danger_soft": "#FCEBEB",
    "warning": "#BA7517",
    "warning_soft": "#FAEEDA",
    "success": "#0F6E56",
    "success_soft": "#E1F5EE",
    "info": "#0C447C",
    "info_soft": "#E6F1FB",
    "radius": 8,
    "density": 12,
    "hero_size": 24,
    "body_size": 14,
    "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    "mono": "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}


THEME_PRESETS = {
    "Courtroom Noir": COURTROOM_NOIR,
    "Courtroom Daylight": COURTROOM_DAYLIGHT,
    "Figma courtroom": FIGMA_COURTROOM,
}


def default_theme() -> dict:
    return deepcopy(THEME_PRESETS["Courtroom Noir"])


def init_theme_state() -> None:
    if THEME_STATE_KEY not in st.session_state:
        st.session_state[THEME_STATE_KEY] = default_theme()
    if MODE_STATE_KEY not in st.session_state:
        st.session_state[MODE_STATE_KEY] = st.session_state[THEME_STATE_KEY].get("mode", "dark")
    if "ui_workspace" not in st.session_state:
        st.session_state.ui_workspace = "Product UI"


def get_theme() -> dict:
    init_theme_state()
    return st.session_state[THEME_STATE_KEY]


def set_theme(theme: dict) -> None:
    st.session_state[THEME_STATE_KEY] = deepcopy(theme)
    st.session_state[MODE_STATE_KEY] = theme.get("mode", "dark")


def set_mode(mode: str) -> None:
    """Switch dark <-> light by swapping in the matching preset."""
    if mode == "light":
        set_theme(THEME_PRESETS["Courtroom Daylight"])
    else:
        set_theme(THEME_PRESETS["Courtroom Noir"])


def get_mode() -> str:
    return st.session_state.get(MODE_STATE_KEY, "dark")


def render_theme_controls() -> str:
    """Render sidebar controls and return the selected workspace."""

    init_theme_state()
    workspace = st.radio(
        "Workspace",
        ["Product UI", "Visual UI Studio"],
        key="ui_workspace",
        horizontal=False,
    )

    expanded = workspace == "Visual UI Studio"
    with st.expander("Design tokens", expanded=expanded):
        preset_name = st.selectbox("Preset", list(THEME_PRESETS.keys()), key="theme_preset")
        if st.button("Apply preset", use_container_width=True):
            set_theme(THEME_PRESETS[preset_name])
            st.rerun()

        theme = get_theme()
        c1, c2 = st.columns(2)
        with c1:
            theme["background"] = st.color_picker("Background", theme["background"])
            theme["surface"] = st.color_picker("Surface", theme["surface"])
            theme["text"] = st.color_picker("Text", theme["text"])
            theme["primary"] = st.color_picker("Primary", theme["primary"])
        with c2:
            theme["surface_muted"] = st.color_picker("Muted surface", theme["surface_muted"])
            theme["border"] = st.color_picker("Border", theme["border"])
            theme["muted_text"] = st.color_picker("Muted text", theme["muted_text"])
            theme["accent"] = st.color_picker("Accent", theme["accent"])

        theme["radius"] = st.slider("Radius", 0, 24, int(theme["radius"]))
        theme["density"] = st.slider("Density", 6, 24, int(theme["density"]))
        theme["hero_size"] = st.slider("Hero title size", 22, 44, int(theme["hero_size"]))
        theme["body_size"] = st.slider("Body text size", 12, 18, int(theme["body_size"]))
        theme["font"] = st.text_input("Font stack", theme["font"])

    return workspace


def _css_vars(theme: dict) -> str:
    return "\n".join(
        [
            f"  --aa-bg: {theme['background']};",
            f"  --aa-bg-grain: {theme.get('background_grain', theme['background'])};",
            f"  --aa-surface: {theme['surface']};",
            f"  --aa-surface-elev: {theme.get('surface_elevated', theme['surface'])};",
            f"  --aa-surface-muted: {theme['surface_muted']};",
            f"  --aa-text: {theme['text']};",
            f"  --aa-text-strong: {theme.get('text_strong', theme['text'])};",
            f"  --aa-muted-text: {theme['muted_text']};",
            f"  --aa-subtle: {theme.get('subtle_text', theme['muted_text'])};",
            f"  --aa-border: {theme['border']};",
            f"  --aa-border-strong: {theme.get('border_strong', theme['border'])};",
            f"  --aa-primary: {theme['primary']};",
            f"  --aa-primary-strong: {theme.get('primary_strong', theme['primary'])};",
            f"  --aa-primary-soft: {theme.get('primary_soft', 'rgba(99,102,241,0.18)')};",
            f"  --aa-primary-glow: {theme.get('primary_glow', 'rgba(99,102,241,0.35)')};",
            f"  --aa-accent: {theme['accent']};",
            f"  --aa-accent-soft: {theme['accent_soft']};",
            f"  --aa-danger: {theme.get('danger', '#EF4444')};",
            f"  --aa-danger-soft: {theme.get('danger_soft', 'rgba(239,68,68,0.14)')};",
            f"  --aa-warning: {theme.get('warning', '#F59E0B')};",
            f"  --aa-warning-soft: {theme.get('warning_soft', 'rgba(245,158,11,0.14)')};",
            f"  --aa-success: {theme.get('success', '#10B981')};",
            f"  --aa-success-soft: {theme.get('success_soft', 'rgba(16,185,129,0.14)')};",
            f"  --aa-info: {theme.get('info', '#38BDF8')};",
            f"  --aa-info-soft: {theme.get('info_soft', 'rgba(56,189,248,0.14)')};",
            f"  --aa-radius: {int(theme['radius'])}px;",
            f"  --aa-radius-sm: {max(4, int(theme['radius']) - 4)}px;",
            f"  --aa-radius-lg: {int(theme['radius']) + 6}px;",
            f"  --aa-density: {int(theme['density'])}px;",
            f"  --aa-hero-size: {int(theme['hero_size'])}px;",
            f"  --aa-body-size: {int(theme['body_size'])}px;",
            f"  --aa-font: {theme['font']};",
            f"  --aa-mono: {theme.get('mono', 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace')};",
        ]
    )


def export_theme_css(theme: dict | None = None) -> str:
    theme = theme or get_theme()
    return f""":root {{
{_css_vars(theme)}
}}"""


def apply_theme(theme: dict | None = None) -> None:
    theme = theme or get_theme()
    is_dark = theme.get("mode") == "dark"
    scrollbar_thumb = "rgba(146,152,168,0.25)" if is_dark else "rgba(15,23,42,0.20)"
    scrollbar_thumb_hover = "rgba(146,152,168,0.45)" if is_dark else "rgba(15,23,42,0.40)"
    sidebar_bg = "#0D0F15" if is_dark else "#F1F4F8"
    grad_overlay = (
        "radial-gradient(1200px 600px at 12% -10%, rgba(99,102,241,0.18), transparent 60%),"
        "radial-gradient(900px 500px at 110% 10%, rgba(245,158,11,0.10), transparent 60%)"
        if is_dark
        else
        "radial-gradient(1200px 600px at 12% -10%, rgba(79,70,229,0.10), transparent 60%),"
        "radial-gradient(900px 500px at 110% 10%, rgba(217,119,6,0.06), transparent 60%)"
    )

    # NOTE: emit via st.html, not st.markdown. Markdown treats any line indented
    # 4+ spaces as a code block — which is why a previous version of this file
    # rendered the entire stylesheet as visible text. textwrap.dedent removes the
    # 8-space Python indent so <style> ends up at column 0, and st.html bypasses
    # the markdown engine entirely. <link> tags get sanitized away by Streamlit,
    # so fonts are loaded via @import inside the <style> block.
    _css = textwrap.dedent(f"""\
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
        :root {{
        {_css_vars(theme)}
          --aa-shadow-sm: 0 1px 2px rgba(0,0,0,{0.35 if is_dark else 0.04});
          --aa-shadow-md: 0 4px 14px rgba(0,0,0,{0.40 if is_dark else 0.06}),
                          0 1px 3px rgba(0,0,0,{0.30 if is_dark else 0.04});
          --aa-shadow-lg: 0 18px 40px rgba(0,0,0,{0.55 if is_dark else 0.10}),
                          0 2px 6px rgba(0,0,0,{0.35 if is_dark else 0.06});
          --aa-shadow-glow: 0 0 0 1px var(--aa-primary-soft),
                            0 12px 30px var(--aa-primary-glow);
        }}

        /* ------------------------------------------------------- base */
        html, body, [class*="css"] {{
            font-family: var(--aa-font);
            color: var(--aa-text);
            font-size: var(--aa-body-size);
            -webkit-font-smoothing: antialiased;
        }}

        .stApp {{
            background:
              {grad_overlay},
              var(--aa-bg);
            color: var(--aa-text);
        }}

        /* Header: keep visible & interactive so the "reopen sidebar" button is
           always reachable. We only strip its background/decoration, never its
           height or pointer-events — collapsing it to 0px was hiding the
           collapsed-control button once the user closed the sidebar. */
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        [data-testid="stHeader"]::before {{
            background: transparent !important;
        }}
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {{ display: none !important; }}

        /* Sidebar reopen button — covers both legacy (collapsedControl) and
           current (stSidebarCollapsedControl) Streamlit test-ids. Pinned to
           the viewport so header height never affects reachability. */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            top: 12px;
            left: 12px;
            z-index: 999999;
            background: var(--aa-surface-elev) !important;
            border: 1px solid var(--aa-border) !important;
            border-radius: 8px !important;
            box-shadow: var(--aa-shadow-md);
            pointer-events: auto !important;
        }}
        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {{
            color: var(--aa-text) !important;
            fill: var(--aa-text) !important;
            pointer-events: auto !important;
        }}

        /* ------------------------------------------ scrollbars */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: {scrollbar_thumb};
            border-radius: 8px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: {scrollbar_thumb_hover}; }}

        /* ------------------------------------------ sidebar */
        [data-testid="stSidebar"] {{
            background: {sidebar_bg};
            border-right: 1px solid var(--aa-border);
            color: var(--aa-text);
            width: 244px !important;
            min-width: 244px !important;
        }}
        [data-testid="stSidebar"] * {{ color: var(--aa-text); }}
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {{
            font-family: var(--aa-font);
            color: var(--aa-text) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] {{
            background: transparent;
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
        }}
        [data-testid="stSidebar"] [data-testid="stExpander"] summary,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * {{
            background: transparent !important;
            color: var(--aa-text) !important;
        }}

        /* ------------------------------------------ main container */
        .block-container {{
            padding: 0 28px 40px;
            max-width: 1280px;
        }}

        h1, h2, h3, h4, h5 {{
            color: var(--aa-text-strong);
            letter-spacing: -0.01em;
            font-weight: 700;
        }}
        h4 {{ font-size: 15px; margin: 0 0 8px; }}
        p, li, label, span {{ color: inherit; }}

        /* ------------------------------------------ buttons */
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {{
            background: var(--aa-surface);
            color: var(--aa-text);
            border: 1px solid var(--aa-border);
            border-radius: 10px;
            min-height: 36px;
            font-size: 13px;
            font-weight: 500;
            transition: all 160ms ease;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {{
            border-color: var(--aa-border-strong);
            background: var(--aa-surface-elev);
            transform: translateY(-1px);
        }}
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {{
            background: linear-gradient(135deg, var(--aa-primary), var(--aa-primary-strong));
            color: #ffffff;
            border-color: transparent;
            box-shadow: 0 6px 18px var(--aa-primary-glow);
        }}
        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover {{
            filter: brightness(1.05);
            box-shadow: 0 10px 26px var(--aa-primary-glow);
        }}

        /* ------------------------------------------ inputs */
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-baseweb="input"] input,
        [data-baseweb="select"] > div {{
            background: var(--aa-surface) !important;
            border: 1px solid var(--aa-border) !important;
            border-radius: 10px !important;
            color: var(--aa-text) !important;
            font-family: var(--aa-font) !important;
            font-size: 13px !important;
            transition: border-color 160ms ease, box-shadow 160ms ease;
        }}
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stTextInput"] input:focus {{
            border-color: var(--aa-primary) !important;
            box-shadow: 0 0 0 3px var(--aa-primary-soft) !important;
            outline: none !important;
        }}
        [data-testid="stTextArea"] textarea::placeholder {{
            color: var(--aa-subtle) !important;
        }}

        /* ------------------------------------------ tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid var(--aa-border);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--aa-radius-sm) var(--aa-radius-sm) 0 0;
            padding: 9px 14px;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"] p {{
            color: var(--aa-muted-text) !important;
            font-weight: 500;
            font-size: 13px;
        }}
        .stTabs [aria-selected="true"] {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-bottom-color: var(--aa-surface);
            margin-bottom: -1px;
        }}
        .stTabs [aria-selected="true"] p {{
            color: var(--aa-text-strong) !important;
            font-weight: 600;
        }}

        /* ------------------------------------------ metrics */
        [data-testid="stMetric"] {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: var(--aa-density);
        }}
        [data-testid="stMetric"] * {{ color: var(--aa-text) !important; }}
        [data-testid="stMetricDelta"] * {{ color: var(--aa-muted-text) !important; }}

        [data-testid="stRadio"] *,
        [data-testid="stCheckbox"] * {{ color: var(--aa-text) !important; }}

        hr {{ border-color: var(--aa-border); margin: 18px 0; }}

        /* ============================================================
           Brand / sidebar
           ============================================================ */

        .act-brand {{
            display: flex; align-items: center; gap: 12px;
            padding: 8px 0 6px;
        }}
        .act-brand .mark {{
            width: 36px; height: 36px;
            display: grid; place-items: center;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--aa-primary), var(--aa-accent));
            box-shadow: 0 8px 22px var(--aa-primary-glow);
            color: white; font-size: 18px; font-weight: 900;
        }}
        .act-brand-stack {{
            display: flex; flex-direction: column; gap: 2px; line-height: 1.05;
        }}
        .act-brand .name {{
            color: var(--aa-text-strong);
            font-size: 15px; font-weight: 800; letter-spacing: 0.4px;
        }}
        .act-brand .tag {{
            background: var(--aa-primary-soft);
            border-radius: 4px; color: var(--aa-primary-strong);
            font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
            padding: 2px 6px; width: max-content;
        }}
        .act-brand-sub {{
            color: var(--aa-muted-text);
            font-size: 11px; font-style: italic;
            padding: 0 0 14px;
            border-bottom: 1px dashed var(--aa-border);
            margin-bottom: 12px;
        }}

        .act-side-section {{
            color: var(--aa-subtle);
            font-size: 10px;
            letter-spacing: 1.2px;
            margin: 16px -8px 6px;
            padding: 0 8px;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .act-case-link, .act-side-link {{
            align-items: center;
            border-radius: 8px;
            color: var(--aa-muted-text);
            display: flex;
            font-size: 13px;
            gap: 8px;
            margin: 2px -4px;
            padding: 7px 10px;
        }}
        .act-case-link:hover {{ background: var(--aa-surface); color: var(--aa-text); }}
        .act-case-link.active {{ background: var(--aa-primary-soft); color: var(--aa-primary-strong); }}
        .act-dot {{ width:6px; height:6px; border-radius:999px; display:inline-block; }}

        .act-mode-switch {{
            display: flex; gap: 4px;
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: 10px;
            padding: 3px;
            margin-bottom: 10px;
        }}
        .act-mode-switch button {{
            flex: 1;
            background: transparent;
            border: none;
            border-radius: 7px;
            color: var(--aa-muted-text);
            font-size: 12px;
            padding: 6px 8px;
            cursor: pointer;
            transition: all 160ms ease;
        }}

        /* ============================================================
           Landing / upload
           ============================================================ */

        .act-hero-wrap {{
            text-align: center;
            padding: 40px 0 8px;
        }}
        .act-hero-badge {{
            display: inline-flex;
            align-items: center; gap: 8px;
            padding: 6px 12px;
            border-radius: 999px;
            background: var(--aa-primary-soft);
            color: var(--aa-primary-strong);
            font-size: 12px; font-weight: 600;
            letter-spacing: 0.4px;
            margin-bottom: 14px;
        }}
        .act-hero-title {{
            font-size: 34px;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0 0 8px;
            background: linear-gradient(135deg, var(--aa-text-strong), var(--aa-primary-strong));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        .act-hero-sub {{
            color: var(--aa-muted-text);
            font-size: 15px;
            line-height: 1.55;
            max-width: 540px;
            margin: 0 auto 18px;
        }}
        .act-trust-row {{
            display: flex; justify-content: center;
            gap: 18px; flex-wrap: wrap;
            margin: 8px 0 22px;
        }}
        .act-trust-chip {{
            display: inline-flex; align-items: center; gap: 6px;
            font-size: 12px; color: var(--aa-muted-text);
        }}
        .act-trust-chip b {{ color: var(--aa-text-strong); font-weight: 700; }}

        .act-or {{
            align-items: center;
            color: var(--aa-subtle);
            display: flex;
            font-size: 11px;
            gap: 12px;
            letter-spacing: 1px;
            margin: 18px auto 12px;
            max-width: 600px;
            text-transform: uppercase;
        }}
        .act-or:before, .act-or:after {{
            background: var(--aa-border);
            content: "";
            flex: 1;
            height: 1px;
        }}

        /* file uploader */
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"] {{
            background: var(--aa-surface) !important;
            border: 1.5px dashed var(--aa-border-strong) !important;
            border-radius: 14px !important;
            color: var(--aa-text) !important;
            min-height: 180px !important;
            padding: 26px 24px !important;
            transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
        }}
        [data-testid="stFileUploader"] section:hover,
        [data-testid="stFileUploaderDropzone"]:hover,
        [data-testid="stFileUploader"] section:focus-within,
        [data-testid="stFileUploaderDropzone"]:focus-within {{
            background: var(--aa-surface-elev) !important;
            border-color: var(--aa-primary) !important;
            box-shadow: 0 0 0 4px var(--aa-primary-soft);
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] > div,
        [data-testid="stFileUploaderDropzoneInstructions"] span {{
            color: var(--aa-text) !important;
            font-weight: 600;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] small,
        [data-testid="stFileUploader"] small {{
            color: var(--aa-muted-text) !important;
            font-weight: 400;
        }}
        [data-testid="stFileUploader"] button {{
            background: linear-gradient(135deg, var(--aa-primary), var(--aa-primary-strong)) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600;
            border-radius: 8px !important;
        }}

        .act-quickstart {{
            display: flex; gap: 10px; flex-wrap: wrap;
            justify-content: center;
            margin: 16px auto 6px;
            max-width: 600px;
        }}
        .act-quickstart-chip {{
            display: inline-flex; align-items: center; gap: 8px;
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: 999px;
            padding: 7px 14px;
            font-size: 12px;
            color: var(--aa-muted-text);
        }}

        /* ============================================================
           Top bar / case file header
           ============================================================ */

        .act-topbar {{
            display: flex; align-items: center; justify-content: space-between;
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 12px 18px;
            margin-bottom: 14px;
            box-shadow: var(--aa-shadow-sm);
        }}
        .act-top-title {{
            display:flex; align-items:center; gap: 10px;
            color: var(--aa-text-strong); font-weight: 600; font-size: 14px;
        }}
        .act-top-actions {{ display:flex; gap: 8px; }}
        .act-mini-button {{
            display:inline-flex; align-items:center; gap: 6px;
            border: 1px solid var(--aa-border);
            border-radius: 8px;
            color: var(--aa-muted-text);
            font-size: 12px;
            padding: 5px 11px;
            background: var(--aa-surface-elev);
        }}
        .act-status-pill {{
            display:inline-flex; align-items:center; gap: 6px;
            background: var(--aa-primary-soft);
            border: 1px solid var(--aa-primary-soft);
            border-radius: 999px;
            color: var(--aa-primary-strong);
            font-size: 11px; font-weight: 600;
            padding: 4px 10px; letter-spacing: 0.3px;
        }}

        .act-case-banner {{
            background:
              linear-gradient(180deg, var(--aa-surface), var(--aa-surface-elev));
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 14px 18px;
            margin-bottom: 14px;
            box-shadow: var(--aa-shadow-md);
            display: flex; align-items: center; justify-content: space-between;
            gap: 16px;
            position: sticky; top: 0; z-index: 50;
        }}
        .act-case-title {{
            display: flex; align-items: center; gap: 10px;
            color: var(--aa-text-strong); font-weight: 600; font-size: 14px;
            min-width: 0;
        }}
        .act-case-title .filename {{
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            max-width: 380px;
        }}
        .act-case-actions {{ display:flex; gap: 8px; flex-shrink: 0; }}

        .act-case-icon {{
            width: 30px; height: 30px;
            display: grid; place-items: center;
            border-radius: 8px;
            background: var(--aa-primary-soft);
            color: var(--aa-primary-strong);
            font-weight: 800;
            flex-shrink: 0;
        }}

        /* ============================================================
           Section titles
           ============================================================ */
        .act-section-title {{
            align-items: center;
            color: var(--aa-text-strong);
            display: flex;
            font-size: 15px;
            font-weight: 700;
            gap: 10px;
            margin: 22px 0 10px;
        }}
        .act-section-title .icon {{
            width: 22px; height: 22px;
            display: grid; place-items: center;
            border-radius: 6px;
            background: var(--aa-primary-soft);
            color: var(--aa-primary-strong);
            font-size: 12px; font-weight: 800;
        }}
        .act-section-title .count {{
            color: var(--aa-muted-text);
            font-size: 12px;
            font-weight: 500;
        }}

        /* ============================================================
           Verdict hero card
           ============================================================ */
        .act-verdict-card {{
            background:
              radial-gradient(900px 320px at 100% -10%, var(--tier-soft, transparent), transparent 60%),
              var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-left: 3px solid var(--tier-color, var(--aa-accent));
            border-radius: var(--aa-radius-lg);
            padding: 22px 24px;
            box-shadow: var(--aa-shadow-md);
            position: relative;
            overflow: hidden;
        }}
        .act-verdict-card::before {{
            content: ""; position: absolute; inset: 0;
            background: radial-gradient(600px 200px at 0% 0%, var(--tier-soft, transparent), transparent 70%);
            pointer-events: none; opacity: 0.7;
        }}

        .act-verdict-top {{
            display: flex; align-items: center; justify-content: space-between;
            gap: 20px; position: relative; z-index: 1;
        }}
        .act-verdict-tier {{
            display: flex; flex-direction: column; gap: 4px;
        }}
        .act-label {{
            color: var(--aa-subtle);
            font-size: 10px; letter-spacing: 1.2px;
            text-transform: uppercase; font-weight: 700;
        }}
        .act-tier-pill {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 8px 14px;
            background: var(--tier-soft, var(--aa-primary-soft));
            color: var(--tier-color, var(--aa-primary));
            border: 1px solid var(--tier-color, var(--aa-primary));
            border-radius: 999px;
            font-size: 13px; font-weight: 700; letter-spacing: 0.5px;
            text-transform: uppercase;
            width: max-content;
            box-shadow: 0 0 24px var(--tier-soft, transparent);
        }}
        .act-tier-pill .dot {{
            width: 8px; height: 8px;
            background: var(--tier-color); border-radius: 999px;
            box-shadow: 0 0 12px var(--tier-color);
            animation: actPulse 2s ease-in-out infinite;
        }}
        @keyframes actPulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(0.85); }}
        }}

        .act-ring-wrap {{
            display: flex; align-items: center; gap: 14px;
        }}
        .act-ring {{
            width: 86px; height: 86px;
            transform: rotate(-90deg);
        }}
        .act-ring circle {{
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
        }}
        .act-ring .track {{
            stroke: var(--aa-border);
        }}
        .act-ring .fill {{
            stroke: var(--tier-color);
            transition: stroke-dasharray 600ms ease;
            filter: drop-shadow(0 0 6px var(--tier-soft));
        }}
        .act-ring-center {{
            position: absolute;
            display: flex; flex-direction: column; align-items: center;
            color: var(--aa-text-strong);
            font-family: var(--aa-mono);
        }}
        .act-ring-center .score {{ font-size: 22px; font-weight: 700; line-height: 1; }}
        .act-ring-center .out-of {{ font-size: 10px; color: var(--aa-subtle); margin-top: 2px; }}
        .act-ring-block {{ position: relative; width: 86px; height: 86px;
            display: grid; place-items: center;
        }}
        .act-ring-info {{ display: flex; flex-direction: column; gap: 2px; }}
        .act-ring-info .lbl {{ color: var(--aa-subtle); font-size: 10px; letter-spacing: 1.2px;
            text-transform: uppercase; font-weight: 700; }}
        .act-ring-info .val {{ color: var(--aa-text-strong); font-size: 16px; font-weight: 700; }}

        .act-reason {{
            color: var(--aa-text);
            font-size: 13.5px;
            line-height: 1.65;
            margin: 16px 0 14px;
            padding: 14px 16px;
            background: var(--aa-surface-elev);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            position: relative; z-index: 1;
        }}

        .act-missing {{
            display: flex; flex-direction: column; gap: 6px;
            position: relative; z-index: 1;
        }}
        .act-missing-title {{
            color: var(--aa-text-strong);
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 4px;
            display: flex; align-items: center; gap: 8px;
        }}
        .act-missing-title .badge {{
            background: var(--aa-warning-soft);
            color: var(--aa-warning);
            font-size: 11px;
            padding: 1px 7px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .act-missing-item {{
            display: flex; align-items: flex-start; gap: 8px;
            color: var(--aa-muted-text);
            font-size: 12.5px;
            padding: 6px 10px;
            background: var(--aa-surface-muted);
            border: 1px solid var(--aa-border);
            border-radius: 8px;
        }}
        .act-missing-item .checkbox {{
            width: 14px; height: 14px; border-radius: 3px;
            border: 1.5px solid var(--aa-border-strong);
            flex-shrink: 0; margin-top: 1px;
        }}
        .act-missing-item.ok .checkbox {{
            background: var(--aa-success);
            border-color: var(--aa-success);
        }}

        .act-guard {{
            color: var(--aa-subtle);
            font-size: 11px;
            font-style: italic;
            margin-top: 14px;
            padding-top: 12px;
            border-top: 1px dashed var(--aa-border);
            position: relative; z-index: 1;
        }}

        /* ============================================================
           Agent stepper
           ============================================================ */
        .act-stepper {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 8px;
            margin: 14px 0 18px;
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 12px;
        }}
        .act-step {{
            display: flex; flex-direction: column; gap: 6px;
            padding: 8px 6px;
            border-radius: 8px;
            position: relative;
            transition: background 200ms;
        }}
        .act-step .step-row {{
            display: flex; align-items: center; gap: 8px;
        }}
        .act-step .step-dot {{
            width: 22px; height: 22px;
            display: grid; place-items: center;
            border-radius: 999px;
            background: var(--aa-surface-muted);
            border: 1.5px solid var(--aa-border-strong);
            font-size: 11px; font-weight: 700;
            color: var(--aa-muted-text);
            flex-shrink: 0;
        }}
        .act-step.completed .step-dot {{
            background: var(--aa-success-soft);
            border-color: var(--aa-success);
            color: var(--aa-success);
        }}
        .act-step.running .step-dot {{
            background: var(--aa-primary-soft);
            border-color: var(--aa-primary);
            color: var(--aa-primary-strong);
            animation: actPulse 1.4s ease-in-out infinite;
        }}
        .act-step.failed .step-dot {{
            background: var(--aa-danger-soft);
            border-color: var(--aa-danger);
            color: var(--aa-danger);
        }}
        .act-step .step-name {{
            color: var(--aa-text-strong);
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .act-step .step-action {{
            color: var(--aa-muted-text);
            font-size: 11px;
            line-height: 1.35;
            min-height: 28px;
            white-space: normal;
        }}
        .act-step .step-duration {{
            color: var(--aa-subtle);
            font-size: 10px;
            font-family: var(--aa-mono);
        }}

        /* ============================================================
           Evidence board
           ============================================================ */
        .act-evidence-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}
        .act-ev-card {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 12px 14px;
            display: flex; flex-direction: column; gap: 8px;
            transition: all 180ms ease;
        }}
        .act-ev-card:hover {{
            border-color: var(--aa-border-strong);
            box-shadow: var(--aa-shadow-md);
            transform: translateY(-2px);
        }}
        .act-ev-head {{
            display: flex; align-items: center; justify-content: space-between;
            gap: 8px;
        }}
        .act-ev-body {{
            color: var(--aa-text);
            font-size: 13px;
            line-height: 1.5;
        }}
        .act-ev-meta {{
            display: flex; align-items: center; gap: 8px;
            color: var(--aa-subtle);
            font-size: 11px;
        }}
        .act-ev-meta .sep {{ color: var(--aa-border-strong); }}

        .act-code {{
            display: inline-flex; align-items: center;
            border-radius: 5px;
            font-family: var(--aa-mono);
            font-size: 11px; font-weight: 600;
            padding: 2px 7px;
            white-space: nowrap;
            letter-spacing: 0.2px;
        }}
        .act-code.e {{ background: var(--aa-info-soft); color: var(--aa-info); }}
        .act-code.r {{ background: var(--aa-primary-soft); color: var(--aa-primary-strong); }}
        .act-code.a {{ background: var(--aa-warning-soft); color: var(--aa-warning); }}

        .act-strength {{
            border-radius: 4px;
            font-size: 10px; font-weight: 700;
            padding: 2px 7px; letter-spacing: 0.3px;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        .act-strong {{ background: var(--aa-success-soft); color: var(--aa-success); }}
        .act-medium {{ background: var(--aa-warning-soft); color: var(--aa-warning); }}
        .act-weak {{ background: var(--aa-danger-soft); color: var(--aa-danger); }}

        .act-empty {{
            color: var(--aa-muted-text);
            font-size: 13px; font-style: italic;
            padding: 20px;
            text-align: center;
            background: var(--aa-surface-muted);
            border: 1px dashed var(--aa-border);
            border-radius: var(--aa-radius);
        }}

        /* ============================================================
           Symbolic rules
           ============================================================ */
        .act-rules-panel {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            overflow: hidden;
        }}
        .act-rules-head {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 16px;
            background: var(--aa-surface-elev);
            border-bottom: 1px solid var(--aa-border);
            color: var(--aa-text-strong);
            font-size: 13px; font-weight: 600;
        }}
        .act-rules-head .summary {{
            display: flex; gap: 12px; align-items: center;
            font-weight: 500; font-size: 12px;
            color: var(--aa-muted-text);
        }}
        .act-rules-head .summary b {{ color: var(--aa-text-strong); font-weight: 700; }}
        .act-rule-body {{
            display: flex; flex-direction: column; gap: 6px;
            padding: 12px 14px;
        }}
        .act-rule-row {{
            display: grid;
            grid-template-columns: 22px 130px 1fr auto;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            background: var(--aa-surface-elev);
            border: 1px solid var(--aa-border);
            border-radius: 8px;
            font-size: 12.5px;
            transition: background 160ms ease;
        }}
        .act-rule-row:hover {{
            background: var(--aa-surface-muted);
        }}
        .act-rule-row.fired {{
            border-left: 3px solid var(--aa-success);
        }}
        .act-rule-row.inactive {{
            border-left: 3px solid var(--aa-border-strong);
            opacity: 0.78;
        }}
        .act-rule-icon {{
            display: grid; place-items: center;
            width: 22px; height: 22px;
            border-radius: 6px;
            font-weight: 700; font-size: 12px;
        }}
        .act-rule-icon.fired {{ background: var(--aa-success-soft); color: var(--aa-success); }}
        .act-rule-icon.inactive {{ background: var(--aa-surface-muted); color: var(--aa-subtle); }}
        .act-rule-id {{
            color: var(--aa-muted-text);
            font-family: var(--aa-mono);
            font-size: 11px;
        }}
        .act-rule-desc {{
            color: var(--aa-text);
        }}

        /* ============================================================
           Objections
           ============================================================ */
        .act-obj-card {{
            background:
              linear-gradient(180deg, var(--aa-warning-soft), var(--aa-surface));
            border: 1px solid var(--aa-warning);
            border-left: 4px solid var(--aa-warning);
            border-radius: var(--aa-radius);
            padding: 14px 18px;
            margin-bottom: 10px;
            position: relative;
            animation: actSlideIn 280ms ease;
        }}
        @keyframes actSlideIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .act-obj-card.resolved {{
            background: linear-gradient(180deg, var(--aa-success-soft), var(--aa-surface));
            border-color: var(--aa-success);
            border-left-color: var(--aa-success);
        }}
        .act-obj-header {{
            display: flex; align-items: center; gap: 10px;
            color: var(--aa-warning);
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 6px;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }}
        .act-obj-card.resolved .act-obj-header {{ color: var(--aa-success); }}
        .act-obj-gavel {{
            width: 22px; height: 22px;
            display: grid; place-items: center;
            background: var(--aa-warning); color: white;
            border-radius: 5px;
            font-size: 12px; font-weight: 900;
        }}
        .act-obj-card.resolved .act-obj-gavel {{ background: var(--aa-success); }}
        .act-obj-body {{
            color: var(--aa-text);
            font-size: 13px;
            line-height: 1.55;
            margin: 4px 0;
        }}
        .act-obj-action {{
            color: var(--aa-muted-text);
            font-size: 11.5px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px dashed var(--aa-border);
            font-style: italic;
        }}

        /* ============================================================
           Governance checklist
           ============================================================ */
        .act-gov-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 8px;
        }}
        .act-gov-item {{
            display: flex; align-items: flex-start; gap: 10px;
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: 8px;
            color: var(--aa-text);
            font-size: 12.5px;
            padding: 10px 12px;
        }}
        .act-gov-item .gov-check {{
            width: 14px; height: 14px;
            border-radius: 3px;
            border: 1.5px solid var(--aa-border-strong);
            flex-shrink: 0; margin-top: 2px;
        }}
        .act-gov-item.required .gov-check {{
            border-color: var(--aa-primary);
            background: var(--aa-primary-soft);
        }}
        .act-gov-item.required .gov-ref {{
            color: var(--aa-primary-strong);
            font-weight: 600;
        }}
        .act-gov-text {{ display: flex; flex-direction: column; gap: 3px; }}
        .act-gov-ref {{ color: var(--aa-subtle); font-size: 11px; font-family: var(--aa-mono); }}

        /* ============================================================
           Chat
           ============================================================ */
        .act-chat-wrap {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 14px;
            margin-top: 16px;
        }}
        .act-chat-head {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 5px;
            margin: 8px 0 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--aa-border);
        }}
        .act-chat-title {{
            color: var(--aa-text-strong);
            font-size: 15px; font-weight: 700;
            line-height: 1.35;
            display: flex; align-items: center; gap: 8px;
        }}
        .act-chat-hint {{
            color: var(--aa-subtle);
            font-size: 12px;
            line-height: 1.4;
            white-space: normal;
        }}

        [data-testid="stChatMessage"] {{
            background: var(--aa-surface-elev) !important;
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: 10px 12px !important;
            margin-bottom: 8px;
        }}
        [data-testid="stChatMessage"] p {{ color: var(--aa-text) !important; }}

        [data-testid="stChatInput"] {{
            display: none !important;
        }}
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {{
            display: none !important;
        }}
        [data-testid="stChatInput"] > div {{
            background: transparent !important;
        }}
        [data-testid="stChatInput"] textarea {{
            background: var(--aa-surface) !important;
            border: 1px solid var(--aa-border) !important;
            border-radius: 10px !important;
            color: var(--aa-text) !important;
            font-family: var(--aa-font) !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{ color: var(--aa-subtle) !important; }}
        [data-testid="stChatInput"] button {{
            background: linear-gradient(135deg, var(--aa-primary), var(--aa-primary-strong)) !important;
            border-radius: 8px !important;
            color: white !important;
        }}
        [data-testid="stChatInput"] button * {{ color: white !important; }}

        .act-followup-chip {{
            display: flex; align-items: flex-start; gap: 8px;
            width: 100%;
            box-sizing: border-box;
            background: var(--aa-primary-soft);
            color: var(--aa-primary-strong);
            border: 1px solid rgba(129, 140, 248, 0.20);
            border-radius: 8px;
            padding: 9px 11px;
            font-size: 12.5px;
            line-height: 1.4;
            margin: 0 0 8px;
            white-space: normal;
        }}
        .act-followup-stack-label {{
            color: var(--aa-subtle);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            margin: 0 0 7px;
            text-transform: uppercase;
        }}
        [data-testid="stForm"] {{
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            background: var(--aa-surface-muted);
            padding: 10px 10px 12px;
            margin-top: 12px;
        }}
        [data-testid="stForm"] [data-testid="stTextArea"] textarea {{
            min-height: 92px !important;
            resize: vertical;
        }}
        [data-testid="stForm"] .stButton > button {{
            margin-top: 4px;
        }}

        /* ============================================================
           Alerts
           ============================================================ */
        [data-testid="stAlert"] {{
            border-radius: var(--aa-radius);
            border: 1px solid var(--aa-border);
            background: var(--aa-surface) !important;
        }}
        [data-testid="stAlert"] * {{ color: var(--aa-text) !important; }}

        /* Tighter responsive */
        @media (max-width: 960px) {{
            .act-stepper {{ grid-template-columns: repeat(3, 1fr); }}
            .act-verdict-top {{ flex-direction: column; align-items: flex-start; }}
        }}
        @media (max-width: 760px) {{
            .act-case-banner {{
                align-items: flex-start;
                flex-direction: column;
                position: relative;
            }}
            .act-case-title {{
                align-items: flex-start;
                flex-wrap: wrap;
            }}
            .act-case-title .filename {{
                max-width: 210px;
            }}
            .act-case-actions {{
                flex-wrap: wrap;
                width: 100%;
            }}
            .act-stepper {{ grid-template-columns: repeat(2, 1fr); }}
            .act-evidence-grid {{ grid-template-columns: 1fr; }}
        }}
        /* Always-visible fallback button to reopen the sidebar. Streamlit's
           built-in collapsed-control sometimes disappears across versions /
           when localStorage persists a hidden state — this button never does. */
        #act-reopen-sidebar {{
            position: fixed;
            top: 12px;
            left: 12px;
            z-index: 1000000;
            width: 38px;
            height: 38px;
            display: none;
            align-items: center;
            justify-content: center;
            background: var(--aa-surface-elev);
            color: var(--aa-text);
            border: 1px solid var(--aa-border);
            border-radius: 8px;
            box-shadow: var(--aa-shadow-md);
            cursor: pointer;
            font-size: 18px;
            font-weight: 700;
            user-select: none;
            transition: background 160ms ease, transform 160ms ease;
        }}
        #act-reopen-sidebar:hover {{
            background: var(--aa-surface);
            transform: translateY(-1px);
        }}
        </style>
    """)
    st.html(_css)
    _inject_sidebar_reopen_button()


def _inject_sidebar_reopen_button() -> None:
    """Inject a floating ☰ button into the parent document that re-opens the
    sidebar. Uses st.html with unsafe_allow_javascript=True so the script
    actually runs (plain st.html ignores <script>). Robust against Streamlit
    DOM/test-id changes and persisted localStorage collapsed state."""
    st.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;
          if (!doc) return;

          // Idempotent: if a previous render already injected the button, reuse it.
          let btn = doc.getElementById('act-reopen-sidebar');
          if (!btn) {
            btn = doc.createElement('div');
            btn.id = 'act-reopen-sidebar';
            btn.title = 'Show sidebar';
            btn.innerHTML = '&#9776;';
            // Styling lives in apply_theme()'s CSS so the button picks up
            // the active theme (light/dark) automatically — we only set the
            // initial `display` inline so it's hidden until JS confirms the
            // sidebar is actually collapsed.
            btn.style.display = 'none';
            doc.body.appendChild(btn);

            btn.addEventListener('click', function () {
              const selectors = [
                '[data-testid="stSidebarCollapsedControl"] button',
                '[data-testid="stSidebarCollapsedControl"]',
                '[data-testid="collapsedControl"] button',
                '[data-testid="collapsedControl"]',
                '[data-testid="stSidebarCollapseButton"] button',
                '[data-testid="stSidebarCollapseButton"]',
              ];
              for (const s of selectors) {
                const el = doc.querySelector(s);
                if (el) { el.click(); return; }
              }
              // Final fallback: clear persisted collapsed state and reload.
              try { window.parent.localStorage.clear(); } catch (e) {}
              window.parent.location.reload();
            });
          }

          function sidebarCollapsed() {
            const sb = doc.querySelector('[data-testid="stSidebar"]');
            if (!sb) return true;
            const aria = sb.getAttribute('aria-expanded');
            if (aria === 'false') return true;
            const r = sb.getBoundingClientRect();
            return r.width < 20 || r.right <= 0;
          }

          function refresh() {
            btn.style.display = sidebarCollapsed() ? 'flex' : 'none';
          }
          refresh();
          if (!window.parent.__actReopenInterval) {
            window.parent.__actReopenInterval = setInterval(refresh, 400);
          }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_token_export() -> None:
    theme = get_theme()
    st.markdown("#### Token CSS")
    st.code(export_theme_css(theme), language="css")
    st.download_button(
        "Download CSS tokens",
        export_theme_css(theme),
        file_name="objection-ui-theme.css",
        mime="text/css",
        use_container_width=True,
    )
