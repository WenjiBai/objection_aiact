"""Visual theme controls for the Streamlit UI."""

from __future__ import annotations

from copy import deepcopy

import streamlit as st


THEME_STATE_KEY = "ui_theme_tokens"

THEME_PRESETS = {
    "Figma courtroom": {
        "background": "#fbfaf8",
        "surface": "#ffffff",
        "surface_muted": "#f5f4f1",
        "text": "#1c1b1f",
        "muted_text": "#605d66",
        "primary": "#534AB7",
        "accent": "#BA7517",
        "accent_soft": "#EEEDFE",
        "border": "#d8d5dd",
        "radius": 8,
        "density": 12,
        "hero_size": 24,
        "body_size": 14,
        "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    },
    "Nordic audit": {
        "background": "#edf2f4",
        "surface": "#ffffff",
        "surface_muted": "#dfe7ea",
        "text": "#182024",
        "muted_text": "#5f6f77",
        "primary": "#11363f",
        "accent": "#2f9c95",
        "accent_soft": "#cbe9e6",
        "border": "#c8d4d8",
        "radius": 6,
        "density": 12,
        "hero_size": 28,
        "body_size": 15,
        "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    },
    "Evidence lab": {
        "background": "#f7f7fb",
        "surface": "#ffffff",
        "surface_muted": "#e8e8f1",
        "text": "#171723",
        "muted_text": "#626274",
        "primary": "#25223d",
        "accent": "#e0aa24",
        "accent_soft": "#f8e7b7",
        "border": "#d9d8e4",
        "radius": 4,
        "density": 10,
        "hero_size": 27,
        "body_size": 14,
        "font": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    },
}


def default_theme() -> dict:
    return deepcopy(THEME_PRESETS["Figma courtroom"])


def init_theme_state() -> None:
    if THEME_STATE_KEY not in st.session_state:
        st.session_state[THEME_STATE_KEY] = default_theme()
    if "ui_workspace" not in st.session_state:
        st.session_state.ui_workspace = "Product UI"


def get_theme() -> dict:
    init_theme_state()
    return st.session_state[THEME_STATE_KEY]


def set_theme(theme: dict) -> None:
    st.session_state[THEME_STATE_KEY] = deepcopy(theme)


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

        theme["accent_soft"] = st.color_picker("Soft accent", theme["accent_soft"])
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
            f"  --aa-surface: {theme['surface']};",
            f"  --aa-surface-muted: {theme['surface_muted']};",
            f"  --aa-text: {theme['text']};",
            f"  --aa-muted-text: {theme['muted_text']};",
            f"  --aa-primary: {theme['primary']};",
            f"  --aa-accent: {theme['accent']};",
            f"  --aa-accent-soft: {theme['accent_soft']};",
            f"  --aa-border: {theme['border']};",
            f"  --aa-radius: {int(theme['radius'])}px;",
            f"  --aa-density: {int(theme['density'])}px;",
            f"  --aa-hero-size: {int(theme['hero_size'])}px;",
            f"  --aa-body-size: {int(theme['body_size'])}px;",
            f"  --aa-font: {theme['font']};",
        ]
    )


def export_theme_css(theme: dict | None = None) -> str:
    theme = theme or get_theme()
    return f""":root {{
{_css_vars(theme)}
}}"""


def apply_theme(theme: dict | None = None) -> None:
    theme = theme or get_theme()
    st.markdown(
        f"""
        <style>
        :root {{
        {_css_vars(theme)}
        }}

        html, body, [class*="css"] {{
            font-family: var(--aa-font);
            color: var(--aa-text);
            font-size: var(--aa-body-size);
        }}

        .stApp {{
            background: var(--aa-bg);
            color: var(--aa-text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: var(--aa-surface-muted);
            border-right: 0.5px solid var(--aa-border);
            color: var(--aa-text);
            width: 220px !important;
            min-width: 220px !important;
        }}

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {{
            font-family: var(--aa-font);
            color: var(--aa-text) !important;
        }}

        [data-testid="stSidebar"] span {{
            color: var(--aa-text) !important;
        }}

        [data-testid="stSidebar"] span[class*="material"],
        span[class*="material-symbols"] {{
            font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
            font-weight: normal !important;
            letter-spacing: normal !important;
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] {{
            background: transparent;
            border: 1px solid var(--aa-border);
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] summary,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * {{
            background: var(--aa-surface-muted) !important;
            color: var(--aa-text) !important;
        }}

        .block-container {{
            padding: 0 24px 24px;
            max-width: 1180px;
        }}

        h1, h2, h3, h4 {{
            color: var(--aa-text);
            letter-spacing: 0;
        }}

        p, li, label, span {{
            color: inherit;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 6px;
            border: 0.5px solid var(--aa-border);
            background: var(--aa-surface);
            color: var(--aa-text);
            min-height: 32px;
            font-size: 13px;
        }}

        .stButton > button[kind="primary"] {{
            background: var(--aa-primary);
            color: white;
            border-color: var(--aa-primary);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 1px solid var(--aa-border);
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: var(--aa-radius) var(--aa-radius) 0 0;
            padding: 8px 12px;
        }}

        .stTabs [data-baseweb="tab"] p {{
            color: var(--aa-muted-text) !important;
        }}

        .stTabs [aria-selected="true"] p {{
            color: var(--aa-accent) !important;
            font-weight: 700;
        }}

        [data-testid="stMetric"],
        [data-testid="stExpander"],
        [data-testid="stAlert"] {{
            border-radius: var(--aa-radius);
        }}

        [data-testid="stMetric"] {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            padding: var(--aa-density);
        }}

        [data-testid="stMetric"] * {{
            color: var(--aa-text) !important;
        }}

        [data-testid="stMetricDelta"] * {{
            color: var(--aa-muted-text) !important;
        }}

        [data-testid="stRadio"] p,
        [data-testid="stRadio"] label,
        [data-testid="stRadio"] span {{
            color: var(--aa-text) !important;
        }}

        hr {{
            border-color: var(--aa-border);
            margin: calc(var(--aa-density) * 1.4) 0;
        }}

        .aa-hero {{
            padding: calc(var(--aa-density) * 1.25) calc(var(--aa-density) * 1.6);
            border-radius: var(--aa-radius);
            background: linear-gradient(135deg, var(--aa-primary), color-mix(in srgb, var(--aa-primary) 72%, var(--aa-accent)));
            color: white;
            border: 1px solid color-mix(in srgb, var(--aa-accent) 50%, transparent);
            box-shadow: 0 16px 38px color-mix(in srgb, var(--aa-primary) 18%, transparent);
        }}

        .aa-hero-title {{
            color: white;
            font-size: var(--aa-hero-size);
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: 0;
        }}

        .aa-hero-subtitle {{
            color: color-mix(in srgb, white 82%, var(--aa-accent-soft));
            font-size: 13px;
            margin-top: 6px;
        }}

        .aa-card,
        .aa-verdict,
        .aa-token-card {{
            background: var(--aa-surface);
            border: 1px solid var(--aa-border);
            border-radius: var(--aa-radius);
            padding: var(--aa-density);
        }}

        .aa-verdict {{
            border-left: 6px solid var(--tier-color, var(--aa-accent));
            margin-bottom: 8px;
        }}

        .aa-verdict-title {{
            color: var(--tier-color, var(--aa-accent));
            font-size: 18px;
            font-weight: 800;
        }}

        .aa-tier-pill {{
            background: var(--tier-color, var(--aa-primary));
            color: white;
            padding: 10px 14px;
            border-radius: var(--aa-radius);
            text-align: center;
            font-weight: 900;
        }}

        .aa-muted {{
            color: var(--aa-muted-text);
        }}

        .aa-swatch {{
            height: 54px;
            border-radius: var(--aa-radius);
            border: 1px solid var(--aa-border);
        }}

        .aa-component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }}

        .act-brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 0 16px;
        }}

        .act-brand .mark {{
            color: var(--aa-primary);
            font-size: 20px;
        }}

        .act-brand .name {{
            color: var(--aa-text);
            font-size: 15px;
            font-weight: 600;
        }}

        .act-brand .tag {{
            background: var(--aa-accent-soft);
            border-radius: 4px;
            color: var(--aa-primary);
            font-size: 11px;
            padding: 2px 6px;
        }}

        .act-side-link,
        .act-case-link {{
            align-items: center;
            border-radius: 0;
            color: var(--aa-muted-text);
            display: flex;
            font-size: 13px;
            gap: 8px;
            margin: 0 -16px;
            padding: 8px 16px;
        }}

        .act-side-link.active,
        .act-case-link.active {{
            background: var(--aa-accent-soft);
            color: var(--aa-primary);
        }}

        .act-side-section {{
            color: #8a8790;
            font-size: 11px;
            letter-spacing: .5px;
            margin: 14px -16px 4px;
            padding: 0 16px;
            text-transform: uppercase;
        }}

        .act-dot {{
            border-radius: 999px;
            display: inline-block;
            height: 6px;
            width: 6px;
        }}

        .act-topbar,
        .act-case-banner {{
            align-items: center;
            background: var(--aa-surface-muted);
            border-bottom: 0.5px solid var(--aa-border);
            display: flex;
            justify-content: space-between;
            margin: 0 -24px 0;
            min-height: 48px;
            padding: 12px 24px;
        }}

        .act-top-title,
        .act-case-title {{
            align-items: center;
            color: var(--aa-text);
            display: flex;
            font-size: 14px;
            font-weight: 600;
            gap: 8px;
        }}

        .act-top-actions,
        .act-case-actions {{
            display: flex;
            gap: 8px;
        }}

        .act-mini-button,
        .act-status-pill {{
            border: 0.5px solid var(--aa-border);
            border-radius: 6px;
            color: var(--aa-muted-text);
            font-size: 12px;
            padding: 4px 10px;
        }}

        .act-status-pill {{
            background: #FAEEDA;
            border: none;
            color: #854F0B;
        }}

        .act-upload-wrap {{
            align-items: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 390px;
            padding: 34px 0 18px;
        }}

        .act-upload-zone {{
            border: 1.5px dashed var(--aa-border);
            border-radius: 10px;
            max-width: 520px;
            padding: 42px 32px 26px;
            text-align: center;
            width: 100%;
        }}

        .act-upload-icon {{
            color: var(--aa-primary);
            font-size: 38px;
            margin-bottom: 12px;
        }}

        .act-upload-title {{
            color: var(--aa-text);
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        .act-upload-sub {{
            color: var(--aa-muted-text);
            font-size: 13px;
            line-height: 1.5;
            margin: 0 auto 14px;
            max-width: 420px;
        }}

        .act-upload-formats {{
            color: #8a8790;
            font-size: 11px;
        }}

        .act-or {{
            align-items: center;
            color: #8a8790;
            display: flex;
            font-size: 12px;
            gap: 12px;
            margin: 20px auto;
            max-width: 520px;
            width: 100%;
        }}

        .act-or:before,
        .act-or:after {{
            background: var(--aa-border);
            content: "";
            flex: 1;
            height: 0.5px;
        }}

        [data-testid="stFileUploader"] {{
            color: var(--aa-text);
        }}

        [data-testid="stFileUploader"] section {{
            background: var(--aa-surface) !important;
            border: 0.5px solid var(--aa-border) !important;
            border-radius: 8px !important;
            color: var(--aa-text) !important;
            min-height: 58px;
        }}

        [data-testid="stFileUploader"] section * {{
            color: var(--aa-muted-text) !important;
        }}

        [data-testid="stFileUploader"] button {{
            background: var(--aa-surface) !important;
            border: 0.5px solid var(--aa-border) !important;
            color: var(--aa-text) !important;
        }}

        [data-testid="stTextArea"] textarea {{
            background: var(--aa-surface) !important;
            border: 0.5px solid var(--aa-border) !important;
            border-radius: 8px !important;
            color: var(--aa-text) !important;
            font-family: var(--aa-font) !important;
            font-size: 13px !important;
        }}

        [data-testid="stTextArea"] textarea::placeholder {{
            color: #8a8790 !important;
        }}

        .act-verdict-card {{
            background: var(--aa-surface);
            border: 0.5px solid var(--aa-border);
            border-left: 3px solid var(--tier-color, var(--aa-accent));
            border-radius: 10px;
            margin-top: 20px;
            padding: 20px;
        }}

        .act-verdict-top {{
            align-items: flex-start;
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 12px;
        }}

        .act-label {{
            color: #8a8790;
            font-size: 11px;
            letter-spacing: .5px;
            margin-bottom: 4px;
            text-transform: uppercase;
        }}

        .act-tier {{
            color: var(--tier-dark, #854F0B);
            font-size: 18px;
            font-weight: 600;
        }}

        .act-confidence {{
            min-width: 190px;
            text-align: right;
        }}

        .act-conf-bar {{
            align-items: center;
            display: flex;
            gap: 2px;
            justify-content: flex-end;
        }}

        .act-conf-seg {{
            background: var(--aa-border);
            border-radius: 2px;
            height: 8px;
            width: 16px;
        }}

        .act-conf-seg.on {{
            background: var(--tier-color, var(--aa-accent));
        }}

        .act-conf-text {{
            color: var(--tier-dark, #854F0B);
            font-size: 11px;
            margin-left: 6px;
            white-space: nowrap;
        }}

        .act-reason {{
            color: var(--aa-muted-text);
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 12px;
        }}

        .act-missing {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .act-missing-title {{
            color: var(--aa-text);
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 2px;
        }}

        .act-missing-item {{
            align-items: center;
            color: var(--aa-muted-text);
            display: flex;
            font-size: 12px;
            gap: 6px;
        }}

        .act-guard {{
            color: #8a8790;
            font-size: 11px;
            font-style: italic;
            margin-top: 10px;
        }}

        .act-section-title {{
            align-items: center;
            color: var(--aa-text);
            display: flex;
            font-size: 14px;
            font-weight: 600;
            gap: 8px;
            margin: 20px 0 8px;
        }}

        .act-section-title .icon {{
            color: var(--aa-primary);
            font-size: 16px;
        }}

        .act-table {{
            border-collapse: collapse;
            font-size: 12px;
            width: 100%;
        }}

        .act-table th {{
            border-bottom: 0.5px solid var(--aa-border);
            color: #8a8790;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: .3px;
            padding: 7px 8px;
            text-align: left;
            text-transform: uppercase;
        }}

        .act-table td {{
            border-bottom: 0.5px solid var(--aa-border);
            color: var(--aa-muted-text);
            padding: 8px;
            vertical-align: top;
        }}

        .act-code {{
            border-radius: 3px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 11px;
            padding: 1px 5px;
            white-space: nowrap;
        }}

        .act-code.e {{ background:#E6F1FB; color:#0C447C; }}
        .act-code.r {{ background:#EEEDFE; color:#3C3489; }}
        .act-code.a {{ background:#FAEEDA; color:#854F0B; }}

        .act-strength {{
            border-radius: 3px;
            font-size: 11px;
            padding: 1px 6px;
            white-space: nowrap;
        }}

        .act-strong {{ background:#E1F5EE; color:#085041; }}
        .act-medium {{ background:#FAEEDA; color:#854F0B; }}
        .act-weak {{ background:#FCEBEB; color:#791F1F; }}

        .act-rules-panel {{
            background: var(--aa-surface-muted);
            border: 0.5px solid var(--aa-border);
            border-radius: 10px;
            overflow: hidden;
        }}

        .act-rules-head {{
            align-items: center;
            color: var(--aa-text);
            display: flex;
            font-size: 13px;
            font-weight: 600;
            justify-content: space-between;
            padding: 10px 16px;
        }}

        .act-rule-body {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding: 0 16px 12px;
        }}

        .act-rule-row {{
            align-items: flex-start;
            background: var(--aa-surface);
            border-radius: 6px;
            display: flex;
            font-size: 12px;
            gap: 8px;
            padding: 7px 8px;
        }}

        .act-rule-id {{
            color: #8a8790;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 11px;
            min-width: 110px;
        }}

        .act-rule-desc {{
            color: var(--aa-muted-text);
            flex: 1;
        }}

        .act-rule-result {{
            border-radius: 3px;
            font-size: 11px;
            padding: 1px 6px;
            white-space: nowrap;
        }}

        .act-obj-card {{
            background: #FAEEDA;
            border: 0.5px solid #EF9F27;
            border-radius: 10px;
            padding: 12px 16px;
        }}

        .act-obj-header {{
            color: #854F0B;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        .act-obj-body {{
            color: #633806;
            font-size: 12px;
            line-height: 1.5;
        }}

        .act-obj-action {{
            color: #854F0B;
            font-size: 11px;
            margin-top: 6px;
        }}

        .act-gov-grid {{
            display: grid;
            gap: 6px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}

        .act-gov-item {{
            align-items: center;
            background: var(--aa-surface-muted);
            border-radius: 6px;
            color: var(--aa-muted-text);
            display: flex;
            font-size: 12px;
            gap: 6px;
            padding: 7px 8px;
        }}

        .act-chat-wrap {{
            background: var(--aa-surface-muted);
            border-top: 0.5px solid var(--aa-border);
            margin: 24px -24px -24px;
            padding: 12px 24px 18px;
        }}

        @media (max-width: 760px) {{
            .act-top-actions,
            .act-case-actions,
            .act-confidence {{
                text-align: left;
            }}
            .act-topbar,
            .act-case-banner,
            .act-verdict-top {{
                align-items: flex-start;
                flex-direction: column;
            }}
            .act-gov-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
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
