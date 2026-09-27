"""SpidyCAD — Stark Suit OS // Emergency Dispatch Triage System.

Multi-Page Architecture with st.session_state Routing:
- Landing Page: Faux-3D Stark / Spider-Verse Hero with interactive 3D particle mesh and massive emergency button.
- Citizen Emergency Portal: Streamlined voice dictation via Web Speech API & massive text area.
- Dispatcher Login: Secure authorization screen (Code: "KAREN-2026").
- Dispatcher Dashboard: Real-time 3s auto-refresh, Pydeck tactical Manhattan radar, P1 Spider-sense danger pulse, and dispatch controls.
"""

import base64
import html
import json
import random
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from PIL import Image
import pydeck as pdk
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# -----------------------------------------------------------------------------
# 1. Page Configuration & Global Constants
# -----------------------------------------------------------------------------
CURRENT_PATH = Path(__file__).resolve()
if CURRENT_PATH.parent.name == "frontend":
    WORKSPACE_ROOT = CURRENT_PATH.parent.parent
else:
    WORKSPACE_ROOT = CURRENT_PATH.parent
IMAGE_DIR = WORKSPACE_ROOT / "image"
TAB_ICON_PATH = IMAGE_DIR / "spidycad-2d-transparent.png"
if not TAB_ICON_PATH.exists():
    TAB_ICON_PATH = IMAGE_DIR / "tab-icon.png"


@st.cache_resource
def ensure_backend_daemon() -> bool:
    """Ensure FastAPI backend is running on 127.0.0.1:8000.
    Launches uvicorn in a background daemon thread if not already running (for Streamlit Cloud)."""
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=0.8)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    def _run():
        try:
            import uvicorn
            from backend import app as fastapi_app
            uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
        except Exception:
            pass

    import threading
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    time.sleep(1.2)
    return True


ensure_backend_daemon()


@st.cache_data(show_spinner=False)
def get_image_base64(filename: str) -> str:
    """Read an image or SVG file from the image/ directory and return a base64 data URI."""
    p = IMAGE_DIR / filename
    if not p.exists():
        return ""
    suffix = p.suffix.lower()
    if suffix == ".svg":
        mime = "image/svg+xml"
    elif suffix in [".png", ".webp"]:
        mime = f"image/{suffix.lstrip('.')}"
    elif suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".ico":
        mime = "image/x-icon"
    else:
        mime = "application/octet-stream"
    encoded = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


try:
    _tab_icon_obj = Image.open(TAB_ICON_PATH) if TAB_ICON_PATH.exists() else "🕸️"
except Exception:
    _tab_icon_obj = "🕸️"

st.set_page_config(
    page_title="SpidyCAD // Team AlgoRhythm",
    page_icon=_tab_icon_obj,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dynamically ensure the browser tab header link rel='icon' uses the high-res SpidyCAD logo
_logo_b64 = get_image_base64("spidycad-logo.png") or get_image_base64("tab-icon.png")
if _logo_b64:
    st.html(
        f"""
        <script>
            (function() {{
                try {{
                    const head = document.head || window.parent.document.head;
                    let link = head.querySelector("link[rel*='icon']");
                    if (!link) {{
                        link = document.createElement('link');
                        link.type = 'image/png';
                        link.rel = 'shortcut icon';
                        head.appendChild(link);
                    }}
                    link.href = "{_logo_b64}";
                }} catch (e) {{}}
            }})();
        </script>
        """
    )

BACKEND_URL = "http://localhost:8000"
REPORTS_URL = f"{BACKEND_URL}/reports"
INGEST_URL = f"{BACKEND_URL}/ingest"

# Default fallback coordinates for known NYC landmarks
NYC_COORDINATES = {
    "times square": (40.7580, -73.9855),
    "midtown": (40.7549, -73.9840),
    "grand central": (40.7527, -73.9772),
    "central market": (40.7527, -73.9772),
    "station road": (40.7516, -73.9755),
    "penn station": (40.7505, -73.9934),
    "penn plaza": (40.7505, -73.9934),
    "chelsea": (40.7465, -74.0014),
    "downtown": (40.7128, -74.0060),
    "financial district": (40.7075, -74.0090),
    "wall street": (40.7075, -74.0090),
    "brooklyn bridge": (40.7061, -73.9969),
    "manhattan bridge": (40.7081, -73.9941),
    "brooklyn": (40.6782, -73.9442),
    "williamsburg": (40.7081, -73.9571),
    "dumbo": (40.7033, -73.9881),
    "queens": (40.7282, -73.7949),
    "queens blvd": (40.7282, -73.8820),
    "long island city": (40.7447, -73.9485),
    "lic plaza": (40.7505, -73.9372),
    "astoria": (40.7644, -73.9235),
    "flushing": (40.7674, -73.8331),
    "manhattan": (40.7831, -73.9712),
    "harlem": (40.8116, -73.9465),
    "central park": (40.7851, -73.9683),
    "bronx": (40.8448, -73.8648),
    "staten island": (40.5795, -74.1502),
    "greenwich village": (40.7336, -74.0027),
    "east village": (40.7265, -73.9815),
    "soho": (40.7233, -74.0030),
    "tribeca": (40.7163, -74.0086),
    "highway": (40.7680, -73.9980),
    "fdr drive": (40.7308, -73.9734),
    "riverside area": (40.7480, -74.0080),
    "riverside": (40.7480, -74.0080),
    "broadway": (40.7590, -73.9845),
    "atlantic avenue": (40.6845, -73.9780),
    "park avenue": (40.7587, -73.9738),
    "bus stand": (40.7570, -73.9900),
    "market": (40.7520, -73.9770),
    "subway": (40.7580, -73.9855),
    "jfk": (40.6413, -73.7781),
    "laguardia": (40.7769, -73.8740),
}

# Major NYC Boroughs and Sub-Areas for manual location entry
NYC_BOROUGHS = {
    "Manhattan": [
        "Midtown Manhattan",
        "Lower Manhattan / Financial District",
        "Times Square / Theater District",
        "Hell's Kitchen",
        "Chelsea",
        "Upper East Side",
        "Upper West Side",
        "Harlem",
        "East Village / Lower East Side",
        "SoHo / Tribeca",
    ],
    "Brooklyn": [
        "Downtown Brooklyn / DUMBO",
        "Williamsburg",
        "Brooklyn Heights",
        "Bushwick",
        "Bedford-Stuyvesant",
        "Park Slope",
        "Coney Island",
        "Crown Heights",
    ],
    "Queens": [
        "Queens Blvd / Elmhurst",
        "Astoria",
        "Long Island City",
        "Flushing",
        "Sunnyside",
        "Jackson Heights",
        "Forest Hills",
        "Jamaica",
    ],
    "Bronx": [
        "South Bronx / Mott Haven",
        "Riverdale",
        "Concourse / Yankee Stadium",
        "Pelham Bay",
        "Fordham",
    ],
    "Staten Island": [
        "St. George",
        "Todt Hill",
        "New Dorp",
        "Great Kills",
        "Tottenville",
    ],
}

# Simulated realistic NYC GPS coordinates for MVP GPS fetch
RANDOM_NYC_COORDINATES = [
    "40.7128, -74.0060",  # Downtown Manhattan
    "40.7580, -73.9855",  # Times Square
    "40.7527, -73.9772",  # Grand Central
    "40.7282, -73.8820",  # Queens Blvd
    "40.7061, -73.9969",  # Brooklyn Bridge
    "40.7680, -73.9980",  # Hell's Kitchen
    "40.8116, -73.9465",  # Harlem
    "40.6782, -73.9442",  # Crown Heights
    "40.7644, -73.9235",  # Astoria
    "40.8448, -73.8648",  # Bronx
]


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely cast value to float, handling None, empty strings, and type errors."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_str(val: Any, default: str = "") -> str:
    """Safely convert value to string, handling None."""
    if val is None:
        return default
    return str(val).strip()


def render_html(raw_html: str) -> None:
    """Render pure HTML directly to the DOM using Streamlit's native st.html, bypassing markdown parsing."""
    clean_html = textwrap.dedent(raw_html).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "citizen_text" not in st.session_state:
    st.session_state.citizen_text = ""
if "location_locked" not in st.session_state:
    st.session_state.location_locked = False
if "locked_location" not in st.session_state:
    st.session_state.locked_location = ""
if "locked_gps_xy" not in st.session_state:
    st.session_state.locked_gps_xy = "None"
if "last_distress_report" not in st.session_state:
    st.session_state.last_distress_report = None
if "gps_coords" not in st.session_state:
    st.session_state.gps_coords = {
        "latitude": 40.7282,
        "longitude": -73.8820,
        "label": "Queens Blvd & Grand Ave (GPS Auto-Locked)",
    }
if "auth_error" not in st.session_state:
    st.session_state.auth_error = False

# -----------------------------------------------------------------------------
# 3. Global CSS — Stark Suit OS & SpidyCAD Tactical HUD Aesthetic
# -----------------------------------------------------------------------------
hex_mesh_bg = get_image_base64("bg-web-hex-mesh.svg")
render_html(
    f"""
    <style>
    .stApp {{
        background-color: #07090F !important;
        background-image: 
            radial-gradient(circle at 92% 5%, rgba(230, 36, 41, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 8% 95%, rgba(0, 128, 255, 0.08) 0%, transparent 45%),
            url('{hex_mesh_bg}') !important;
        background-repeat: repeat !important;
        background-size: auto, auto, 240px 240px !important;
        background-attachment: fixed !important;
    }}
    </style>
    """
)

render_html(
    """
<style>
    /* Dark Obsidian & Slate Root Theme */
    .stApp {
        background-color: #0B0D12;
        color: #F3F4F6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    }

    /* Monospaced Tactical Accents */
    .mono-font {
        font-family: "JetBrains Mono", "SF Mono", Consolas, ui-monospace, monospace;
    }

    /* Custom Spider-Sense Danger Pulse for Priority > 85% */
    @keyframes spidey-sense-pulse {
        0%, 100% {
            box-shadow: 0 0 15px rgba(230, 36, 41, 0.4), inset 0 0 10px rgba(230, 36, 41, 0.2);
            border-color: #E62429;
        }
        50% {
            box-shadow: 0 0 35px rgba(230, 36, 41, 0.8), inset 0 0 20px rgba(230, 36, 41, 0.4);
            border-color: #FF3B30;
        }
    }

    .spidey-pulse-card {
        animation: spidey-sense-pulse 2.2s infinite ease-in-out;
    }

    /* Stark HUD Card Architecture */
    .karen-card {
        background: #12161F;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        position: relative;
        transition: all 0.2s ease-in-out;
    }

    .karen-card:hover {
        border-color: rgba(0, 128, 255, 0.4);
        background: #151A24;
    }

    /* Corner Optics Accents */
    .karen-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 8px;
        height: 8px;
        border-top: 2px solid #0080FF;
        border-left: 2px solid #0080FF;
    }

    .karen-card::after {
        content: "";
        position: absolute;
        bottom: 0;
        right: 0;
        width: 8px;
        height: 8px;
        border-bottom: 2px solid #E62429;
        border-right: 2px solid #E62429;
    }

    /* Card Typography Elements */
    .card-msg-text {
        font-size: 14px;
        color: #F3F4F6;
        line-height: 1.5;
        margin: 10px 0;
        min-height: 40px;
    }

    .card-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
    }

    .card-header-tags {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
    }

    .prio-score-wrap {
        font-size: 18px;
        font-weight: 900;
        white-space: nowrap;
    }

    .card-footer-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 8px;
        margin-top: 8px;
        font-size: 12px;
    }

    .card-loc-meta {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        color: #94A3B8;
    }

    .loc-label {
        color: #E2E8F0;
    }

    .cred-meta {
        color: #94A3B8;
    }

    .cred-val {
        color: #38BDF8;
        font-weight: 700;
    }

    .meta-dot {
        color: #64748B;
    }

    /* Glowing Status Badges */
    .badge-critical {
        background: rgba(230, 36, 41, 0.18);
        color: #FF4D4D;
        border: 1px solid #E62429;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid #F59E0B;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .badge-routine {
        background: rgba(100, 116, 139, 0.15);
        color: #94A3B8;
        border: 1px solid #64748B;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }

    .badge-tech {
        background: rgba(0, 128, 255, 0.15);
        color: #38BDF8;
        border: 1px solid #0080FF;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }

    .badge-dispatched {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid #10B981;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }

    /* Live Queue Header Bar */
    .live-queue-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 12px;
    }

    .live-queue-title {
        font-size: 18px;
        font-weight: 800;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
    }

    .live-queue-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: monospace;
        font-size: 12px;
        color: #94A3B8;
    }

    /* Streamlit Widget Overrides */
    div[data-testid="stSidebarNav"] {
        display: none;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #12161F !important;
        color: #F3F4F6 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 6px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E62429 !important;
        box-shadow: 0 0 10px rgba(230, 36, 41, 0.3) !important;
    }

    .disabled-input-msg {
        background: rgba(230, 36, 41, 0.1);
        border: 1px dashed #E62429;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #FF6B6B;
        font-family: monospace;
        margin-bottom: 12px;
    }

    /* Responsive App Container Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        padding-left: clamp(1rem, 3.5vw, 2.5rem) !important;
        padding-right: clamp(1rem, 3.5vw, 2.5rem) !important;
        max-width: 1400px !important;
    }

    /* Fluid Top Header Bar */
    .hud-top-bar {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 14px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .hud-top-left {
        flex: 1 1 320px;
    }

    .hud-top-right {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: 8px;
    }

    .hud-main-title {
        font-size: clamp(20px, 3.2vw, 28px) !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.25 !important;
        color: #FFFFFF !important;
    }

    /* Responsive Grid for Columns */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
    }

    /* Allow columns to wrap and maintain minimum readable width */
    @media (max-width: 960px) {
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 calc(50% - 12px) !important;
            min-width: 250px !important;
        }
    }

    @media (max-width: 640px) {
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

    /* Hide default sidebar completely to give full 100% width to tactical HUD */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
</style>
    """
)


# -----------------------------------------------------------------------------
# 4. Global Top Navigation Bar — Stark OS Tactical Command Header
# -----------------------------------------------------------------------------
def render_top_navigation_bar() -> None:
    """Render the sticky, high-tech Stark top navigation bar across all views."""
    current_p = st.session_state.page
    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")

    nav_col_brand, nav_col_btn1, nav_col_btn2, nav_col_btn3, nav_col_status = st.columns(
        [2.6, 1.25, 1.35, 1.45, 1.25]
    )

    with nav_col_brand:
        render_html(
            f"""
            <div style="display: flex; align-items: center; gap: 14px; padding: 2px 0;">
                <img src="{icon_b64}" style="width: 48px; height: 48px; border-radius: 12px; border: 1.5px solid rgba(255, 51, 75, 0.85); box-shadow: 0 0 20px rgba(255, 51, 75, 0.5), 0 0 35px rgba(56, 189, 248, 0.25); background: #070b14; object-fit: contain;" alt="SpidyCAD Logo" />
                <div>
                    <div style="font-size: 22px; font-weight: 900; color: #FFFFFF; line-height: 1.1; letter-spacing: -0.5px;">
                        Spidy<span style="color: #FF334B;">CAD</span>
                    </div>
                    <div style="font-family: monospace; font-size: 10px; color: #38BDF8; letter-spacing: 1.5px; font-weight: 700;">
                        TEAM ALGORHYTHM // HUD
                    </div>
                </div>
            </div>
            """
        )

    with nav_col_btn1:
        if st.button(
            "🌐 Comms Hub",
            key="top_nav_hub",
            use_container_width=True,
            type="primary" if current_p == "landing" else "secondary",
        ):
            st.session_state.page = "landing"
            st.rerun()

    with nav_col_btn2:
        if st.button(
            "🚨 Citizen Portal",
            key="top_nav_citizen",
            use_container_width=True,
            type="primary" if current_p == "citizen" else "secondary",
        ):
            st.session_state.page = "citizen"
            st.rerun()

    with nav_col_btn3:
        disp_label = "🛡️ Dispatcher HUD" if st.session_state.authenticated else "🛡️ Dispatch Login"
        if st.button(
            disp_label,
            key="top_nav_disp",
            use_container_width=True,
            type="primary" if current_p in ["login", "dashboard"] else "secondary",
        ):
            st.session_state.page = "dashboard" if st.session_state.authenticated else "login"
            st.rerun()

    with nav_col_status:
        if st.session_state.authenticated:
            if st.button("🔒 Logout", key="top_nav_logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.page = "landing"
                st.rerun()
        else:
            render_html(
                """
                <div style="display: flex; align-items: center; justify-content: flex-end; height: 100%; padding-right: 4px;">
                    <div style="font-family: monospace; font-size: 11px; background: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; border-radius: 20px; padding: 6px 14px; color: #34D399; font-weight: bold; white-space: nowrap;">
                        ● RADAR ONLINE
                    </div>
                </div>
                """
            )

    render_html(
        """
        <div style="height: 1px; background: linear-gradient(90deg, rgba(230,36,41,0.6) 0%, rgba(56,189,248,0.4) 50%, rgba(255,255,255,0.08) 100%); margin: 8px 0 20px 0;"></div>
        """
    )


# -----------------------------------------------------------------------------
# 5. VIEW 1: THE LANDING PAGE (Faux-3D Stark / Spider-Verse Hero Aesthetic)
# -----------------------------------------------------------------------------
def render_landing_page() -> None:
    """Render the high-impact landing view with 3D Canvas particle web & massive pulsing emergency button."""
    # Custom CSS specifically targeting the landing page buttons
    render_html(
        """
        <style>
        @keyframes landing-emergency-pulse {
            0%, 100% {
                box-shadow: 0 0 24px rgba(230, 36, 41, 0.75), 0 0 50px rgba(230, 36, 41, 0.45);
                border-color: #FF4D4D;
                transform: scale(1);
            }
            50% {
                box-shadow: 0 0 45px rgba(255, 77, 77, 1), 0 0 85px rgba(230, 36, 41, 0.8);
                border-color: #FFFFFF;
                transform: scale(1.025);
            }
        }

        /* Hero Primary Emergency Button */
        div[data-testid="stButton"] button[kind="primary"],
        div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #E62429 0%, #991B1B 100%) !important;
            color: #FFFFFF !important;
            font-size: 20px !important;
            font-weight: 900 !important;
            letter-spacing: 1px !important;
            padding: 22px 28px !important;
            border-radius: 12px !important;
            border: 2px solid #FF4D4D !important;
            animation: landing-emergency-pulse 2s infinite ease-in-out !important;
            text-transform: uppercase !important;
            cursor: pointer !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover,
        div[data-testid="stButton"] button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #FF3B30 0%, #B91C1C 100%) !important;
            transform: scale(1.04) !important;
        }

        /* Hero Secondary Override Button */
        div[data-testid="stButton"] button[kind="secondary"],
        div[data-testid="stButton"] button[data-testid="baseButton-secondary"] {
            background: rgba(18, 22, 31, 0.95) !important;
            color: #CBD5E1 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            padding: 22px 28px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stButton"] button[kind="secondary"]:hover,
        div[data-testid="stButton"] button[data-testid="baseButton-secondary"]:hover {
            background: #171E2B !important;
            color: #38BDF8 !important;
            border-color: #0080FF !important;
            box-shadow: 0 0 20px rgba(0, 128, 255, 0.35) !important;
            transform: translateY(-2px) !important;
        }
        </style>
        """
    )

    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    render_html(
        f"""
        <div style="text-align: center; padding: 12px 0 22px 0; max-width: 860px; margin: 0 auto;">
            <div style="display: inline-block; margin-bottom: 8px;">
                <img src="{icon_b64}" style="width: 80px; height: 80px; border-radius: 20px; border: 2px solid rgba(255, 51, 75, 0.85); box-shadow: 0 0 35px rgba(255, 51, 75, 0.5), 0 0 50px rgba(56, 189, 248, 0.25); background: #070b14; object-fit: contain;" alt="SpidyCAD Logo" />
            </div>
            <h1 style="font-size: clamp(34px, 5.2vw, 54px); font-weight: 900; color: #FFFFFF; letter-spacing: -1px; margin: 0; line-height: 1.1;">
                Spidy<span style="color: #FF334B;">CAD</span>
            </h1>
            <div style="font-family: monospace; font-size: 13.5px; color: #38BDF8; letter-spacing: 4px; font-weight: 700; margin: 6px 0 4px 0;">
                COMPUTER-AIDED DISPATCH SYSTEM
            </div>
            <p style="font-size: 14.5px; color: #94A3B8; max-width: 660px; margin: 0 auto; line-height: 1.55;">
                Next-generation emergency dispatch, zero-touch NLP incident extraction, and live Manhattan tactical radar triage powered by Stark Suit protocols.
            </p>
            <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-top: 14px;">
                <span class="badge-critical mono-font">🚨 AI 911 INTERCEPT</span>
                <span class="badge-tech mono-font">🛰️ NYC RADAR GRID</span>
                <span class="badge-warning mono-font">⚡ SPIDER-SENSE TRIAGE</span>
                <span class="badge-dispatched mono-font">🕸️ TEAM ALGORHYTHM</span>
            </div>
        </div>
        """
    )

    # 3D Canvas Particle Spiderweb Component via Streamlit Components iframe
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    background: #0B0D12;
                    overflow: hidden;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
                    user-select: none;
                }
                #canvas-wrap {
                    position: relative;
                    width: 100%;
                    height: 385px;
                    background: radial-gradient(circle at 50% 50%, #151D2F 0%, #080A0F 85%);
                    border: 1px solid rgba(0, 128, 255, 0.25);
                    border-radius: 14px;
                    overflow: hidden;
                    box-shadow: inset 0 0 60px rgba(0,0,0,0.8), 0 8px 32px rgba(0,0,0,0.6);
                }
                canvas {
                    display: block;
                    width: 100%;
                    height: 100%;
                }
                .hud-overlay {
                    position: absolute;
                    pointer-events: none;
                }
                .hud-top-left {
                    top: 16px;
                    left: 20px;
                    font-size: 11px;
                    color: #38BDF8;
                    letter-spacing: 1.5px;
                    font-weight: 700;
                    text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
                }
                .hud-top-right {
                    top: 16px;
                    right: 20px;
                    font-size: 11px;
                    color: #E62429;
                    letter-spacing: 1px;
                    font-weight: 700;
                    text-align: right;
                }
                .hud-center {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                    pointer-events: none;
                }
                .hud-hero-title {
                    font-size: 32px;
                    font-weight: 900;
                    color: #FFFFFF;
                    letter-spacing: -0.02em;
                    text-shadow: 0 0 25px rgba(255,255,255,0.4), 0 0 50px rgba(0,128,255,0.4);
                }
                .hud-hero-sub {
                    font-size: 13px;
                    color: #94A3B8;
                    margin-top: 6px;
                    letter-spacing: 2px;
                    font-family: monospace;
                }
                .reticle-ring {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    border-radius: 50%;
                    border: 1px dashed rgba(0, 128, 255, 0.2);
                    pointer-events: none;
                    animation: spin 30s linear infinite;
                }
                @keyframes spin {
                    from { transform: translate(-50%, -50%) rotate(0deg); }
                    to { transform: translate(-50%, -50%) rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div id="canvas-wrap">
                <canvas id="spider-3d"></canvas>
                <div class="reticle-ring" style="width: 280px; height: 280px;"></div>
                <div class="reticle-ring" style="width: 180px; height: 180px; border-style: dotted; border-color: rgba(230, 36, 41, 0.25); animation-direction: reverse;"></div>

                <div class="hud-overlay hud-top-left">
                    <div>● STARK NEURAL MESH // SPIDER-NET 3D</div>
                    <div style="color: #64748B; font-size: 10px; margin-top: 2px;">NODES: 68 ONLINE • LATENCY: 8ms</div>
                </div>

                <div class="hud-overlay hud-top-right">
                    <div>SECTOR: NYC METRO</div>
                    <div style="color: #4ADE80; font-size: 10px; margin-top: 2px;">STATUS: DEFCON 2 ACTIVE</div>
                </div>

                <div class="hud-center">
                    <div class="hud-hero-title">SPIDYCAD</div>
                    <div class="hud-hero-sub">AI EMERGENCY DISPATCH SYSTEM</div>
                </div>
            </div>

            <script>
                const canvas = document.getElementById('spider-3d');
                const ctx = canvas.getContext('2d');
                let width = canvas.width = canvas.offsetWidth;
                let height = canvas.height = canvas.offsetHeight;

                window.addEventListener('resize', () => {
                    width = canvas.width = canvas.offsetWidth;
                    height = canvas.height = canvas.offsetHeight;
                });

                // 3D Particles Generator
                const NUM_PARTICLES = 65;
                const particles = [];
                for (let i = 0; i < NUM_PARTICLES; i++) {
                    const isHazard = (i % 8 === 0);
                    particles.push({
                        x: (Math.random() - 0.5) * 600,
                        y: (Math.random() - 0.5) * 350,
                        z: (Math.random() - 0.5) * 500,
                        vx: (Math.random() - 0.5) * 0.4,
                        vy: (Math.random() - 0.5) * 0.4,
                        vz: (Math.random() - 0.5) * 0.4,
                        isHazard: isHazard,
                        radius: isHazard ? 3.5 : 2.0,
                    });
                }

                let angleX = 0;
                let angleY = 0;
                let mouseX = 0;
                let mouseY = 0;

                window.addEventListener('mousemove', (e) => {
                    const rect = canvas.getBoundingClientRect();
                    mouseX = (e.clientX - rect.left - width / 2) * 0.0005;
                    mouseY = (e.clientY - rect.top - height / 2) * 0.0005;
                });

                function render() {
                    ctx.clearRect(0, 0, width, height);

                    angleY += 0.003 + mouseX * 0.5;
                    angleX += 0.001 + mouseY * 0.5;

                    const cosY = Math.cos(angleY), sinY = Math.sin(angleY);
                    const cosX = Math.cos(angleX), sinX = Math.sin(angleX);

                    const projected = [];

                    for (let i = 0; i < particles.length; i++) {
                        const p = particles[i];
                        p.x += p.vx;
                        p.y += p.vy;
                        p.z += p.vz;

                        if (p.x < -300 || p.x > 300) p.vx *= -1;
                        if (p.y < -180 || p.y > 180) p.vy *= -1;
                        if (p.z < -250 || p.z > 250) p.vz *= -1;

                        // 3D Rotation
                        let x1 = p.x * cosY - p.z * sinY;
                        let z1 = p.z * cosY + p.x * sinY;
                        let y1 = p.y * cosX - z1 * sinX;
                        let z2 = z1 * cosX + p.y * sinX;

                        // Perspective projection
                        const fov = 420;
                        const scale = fov / (fov + z2 + 300);
                        const px = width / 2 + x1 * scale;
                        const py = height / 2 + y1 * scale;

                        projected.push({
                            px, py, scale, z: z2, isHazard: p.isHazard, radius: p.radius
                        });
                    }

                    // Draw connecting spider-filaments
                    for (let i = 0; i < projected.length; i++) {
                        for (let j = i + 1; j < projected.length; j++) {
                            const p1 = projected[i];
                            const p2 = projected[j];
                            const dx = p1.px - p2.px;
                            const dy = p1.py - p2.py;
                            const dist = Math.sqrt(dx * dx + dy * dy);

                            if (dist < 85) {
                                const alpha = (1 - dist / 85) * 0.35 * Math.min(p1.scale, p2.scale);
                                ctx.beginPath();
                                ctx.moveTo(p1.px, p1.py);
                                ctx.lineTo(p2.px, p2.py);
                                if (p1.isHazard || p2.isHazard) {
                                    ctx.strokeStyle = `rgba(230, 36, 41, ${alpha * 1.5})`;
                                    ctx.lineWidth = 1.2;
                                } else {
                                    ctx.strokeStyle = `rgba(0, 128, 255, ${alpha})`;
                                    ctx.lineWidth = 0.8;
                                }
                                ctx.stroke();
                            }
                        }
                    }

                    // Draw Nodes
                    for (let i = 0; i < projected.length; i++) {
                        const p = projected[i];
                        const r = p.radius * p.scale;
                        ctx.beginPath();
                        ctx.arc(p.px, p.py, Math.max(1, r), 0, Math.PI * 2);

                        if (p.isHazard) {
                            ctx.fillStyle = '#FF4D4D';
                            ctx.shadowColor = '#FF3B30';
                            ctx.shadowBlur = 12;
                        } else {
                            ctx.fillStyle = '#38BDF8';
                            ctx.shadowColor = '#0080FF';
                            ctx.shadowBlur = 6;
                        }
                        ctx.fill();
                        ctx.shadowBlur = 0;
                    }

                    requestAnimationFrame(render);
                }

                render();
            </script>
        </body>
        </html>
        """,
        height=410,
        scrolling=False,
    )

    render_html("<div style='height: 14px;'></div>")

    # Layered Massive Action Buttons
    col_em, col_disp = st.columns([1.3, 1])

    with col_em:
        if st.button("🚨 I HAVE AN EMERGENCY", type="primary", use_container_width=True, key="landing_emergency_btn"):
            st.session_state.page = "citizen"
            st.rerun()

    with col_disp:
        if st.button("🛡️ Dispatcher Override", use_container_width=True, key="landing_dispatcher_btn"):
            st.session_state.page = "login"
            st.rerun()

    render_html("<div style='height: 20px;'></div>")

    # Tactical Highlights & Telemetry Info Grid
    f1, f2, f3 = st.columns(3)
    with f1:
        render_html(
            """
            <div class="karen-card">
                <div class="mono-font" style="font-size: 11px; color: #38BDF8; font-weight: 700;">● ZERO-TOUCH NLP</div>
                <div style="font-size: 15px; font-weight: 800; color: #FFFFFF; margin: 4px 0;">Instant Incident Extraction</div>
                <div style="font-size: 13px; color: #94A3B8;">NLP engine detects fire, collapse, accidents, and casualty counts directly from conversational reports.</div>
            </div>
            """
        )
    with f2:
        render_html(
            """
            <div class="karen-card">
                <div class="mono-font" style="font-size: 11px; color: #E62429; font-weight: 700;">● PRIORITY ENGINE</div>
                <div style="font-size: 15px; font-weight: 800; color: #FFFFFF; margin: 4px 0;">Spider-Sense Danger Triage</div>
                <div style="font-size: 13px; color: #94A3B8;">Calculates dynamic urgency and credibility floats (0.00 - 1.00), triggering immediate alerts for P1 hazards (&gt;85%).</div>
            </div>
            """
        )
    with f3:
        render_html(
            """
            <div class="karen-card">
                <div class="mono-font" style="font-size: 11px; color: #34D399; font-weight: 700;">● SECURE INTERLINK</div>
                <div style="font-size: 15px; font-weight: 800; color: #FFFFFF; margin: 4px 0;">First Responder Dispatch</div>
                <div style="font-size: 13px; color: #94A3B8;">Provides authoritative radar mapping, real-time sync, and one-click unit deployment for NY emergency services.</div>
            </div>
            """
        )

    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 36px; padding: 18px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 13px; color: #94A3B8; letter-spacing: 1.2px; display: flex; align-items: center; justify-content: center; gap: 10px;">
            <img src="{icon_b64}" style="width: 24px; height: 24px; border-radius: 6px; vertical-align: middle; object-fit: contain;" alt="SpidyCAD" />
            <span>🕸️ Engineered by <strong style="color: #38BDF8;">Team AlgoRhythm</strong> &nbsp;|&nbsp; SpidyCAD Computer-Aided Dispatch</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 6. VIEW 2: CITIZEN EMERGENCY PORTAL (Streamlined & Speech-to-Text)
# -----------------------------------------------------------------------------
def render_citizen_portal() -> None:
    """Render the citizen emergency portal with instant browser Speech-to-Text and a massive text area."""
    # Top Status Bar with SpidyCAD Icon
    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    render_html(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; background: #0A0F1E; border: 1px solid rgba(0, 128, 255, 0.35); border-radius: 12px; padding: 16px 22px; margin-bottom: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.6); flex-wrap: wrap; gap: 14px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <img src="{icon_b64}" style="width: 58px; height: 58px; border-radius: 12px; border: 1.5px solid rgba(255, 51, 75, 0.85); box-shadow: 0 0 20px rgba(255, 51, 75, 0.45); background: #070b14; object-fit: contain;" alt="SpidyCAD Logo" />
                <div>
                    <div style="margin-bottom: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span class="badge-tech mono-font">CITIZEN DISTRESS CHANNEL</span>
                        <span class="badge-critical mono-font">DIRECT LINK TO SPIDYCAD</span>
                    </div>
                    <h1 style="font-size: 24px; font-weight: 900; color: #FFFFFF; margin: 0; line-height: 1.2;">
                        Spidy<span style="color: #FF334B;">CAD</span> Emergency Assistance
                    </h1>
                    <p style="font-size: 13px; color: #94A3B8; margin: 3px 0 0 0;">
                        Speak or type your emergency below. SpidyCAD extracts incident types and prioritizes rescue units automatically.
                    </p>
                </div>
            </div>
            <div style="text-align: right;" class="mono-font">
                <span class="badge-tech">WEB-SHOOTER COMMS: ONLINE</span>
                <div style="font-size: 11px; color: #34D399; margin-top: 4px; font-weight: bold;">● AI TRIAGE READY</div>
            </div>
        </div>
        """
    )

    col_ret, _ = st.columns([1, 4])
    with col_ret:
        if st.button("← Return to Home", use_container_width=True, key="citizen_back_btn"):
            st.session_state.page = "landing"
            st.rerun()

    # Render confirmation banner if a report was recently submitted
    if st.session_state.last_distress_report:
        report_data = st.session_state.last_distress_report
        prio_val = int(safe_float(report_data.get("priority", 0.5)) * 100)
        rep_id = html.escape(safe_str(report_data.get("report_id", "PENDING")))
        rep_type = html.escape(safe_str(report_data.get("incident_type", "UNKNOWN")).upper())
        rep_loc = html.escape(safe_str(report_data.get("location", "Reported Location")))
        rep_gps = html.escape(safe_str(report_data.get("gps_xy", "None")))

        render_html(
            f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 8px; padding: 18px; margin: 14px 0;">
                <div style="font-size: 15px; font-weight: bold; color: #34D399; font-family: monospace;">
                    🕸️ DISTRESS SIGNAL RECEIVED & TRIAGED BY SPIDYCAD
                </div>
                <div style="font-size: 13.5px; color: #F3F4F6; margin-top: 6px;">
                    Incident Call: <strong>#{rep_id}</strong> &nbsp;|&nbsp; 
                    AI Priority Score: <strong>{prio_val}%</strong> &nbsp;|&nbsp; 
                    Auto-Classified: <strong>{rep_type}</strong>
                </div>
                <div style="font-size: 12.5px; color: #CBD5E1; margin-top: 4px;">
                    <strong>Location:</strong> {rep_loc} &nbsp;|&nbsp; <strong>GPS:</strong> {rep_gps}
                </div>
                <div style="font-size: 12px; color: #94A3B8; margin-top: 6px; line-height: 1.5;">
                    Logged to raw telemetry stream (raw_emergencies.csv). First responder units and Spider-Man protocols have been alerted. Form has been reset for subsequent dispatches.
                </div>
            </div>
            """
        )
        if st.button("✕ Dismiss Confirmation", key="dismiss_confirm_btn"):
            st.session_state.last_distress_report = None
            st.rerun()

    # Step 1: Location Selection (Sequential Lock)
    st.markdown("### 📍 Step 1: Location Selection")

    if not st.session_state.location_locked:
        loc_choice = st.radio(
            "Select Location Method:",
            ["🛰️ Use GPS", "🗺️ Enter Manually"],
            horizontal=True,
            key="citizen_loc_choice",
        )

        if loc_choice == "🗺️ Enter Manually":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                selected_borough = st.selectbox(
                    "Major NYC Borough:",
                    list(NYC_BOROUGHS.keys()),
                    key="manual_borough_select",
                )
            with col_b2:
                selected_subarea = st.selectbox(
                    "Sub-Area / Neighborhood:",
                    NYC_BOROUGHS[selected_borough],
                    key="manual_subarea_select",
                )

            specific_details = st.text_input(
                "Specific Details (e.g., floor, landmark):",
                placeholder="e.g., Floor 3, Apt 4B, near Grand Central terminal",
                key="manual_details_input",
            )

            if st.button("🔒 Lock Location", type="primary", use_container_width=True, key="lock_manual_loc_btn"):
                parts = [selected_borough, selected_subarea]
                if specific_details.strip():
                    parts.append(specific_details.strip())
                loc_str = ", ".join(parts)
                st.session_state.locked_location = loc_str

                # Pre-resolve GPS coordinates from subarea, landmark, or borough
                resolved_gps = "None"
                search_scope = f"{selected_subarea} {selected_borough} {specific_details}".lower()
                for landmark, (l_lat, l_lon) in NYC_COORDINATES.items():
                    if landmark in search_scope:
                        resolved_gps = f"{l_lat:.4f}, {l_lon:.4f}"
                        break
                if resolved_gps == "None":
                    borough_defaults = {
                        "Manhattan": "40.7831, -73.9712",
                        "Brooklyn": "40.6782, -73.9442",
                        "Queens": "40.7282, -73.7949",
                        "Bronx": "40.8448, -73.8648",
                        "Staten Island": "40.5795, -74.1502",
                    }
                    resolved_gps = borough_defaults.get(selected_borough, "40.7580, -73.9855")

                st.session_state.locked_gps_xy = resolved_gps
                st.session_state.location_locked = True
                st.rerun()

        else:  # "🛰️ Use GPS"
            render_html(
                """
                <div style="background: rgba(0, 128, 255, 0.08); border: 1px solid rgba(0, 128, 255, 0.3); border-radius: 6px; padding: 12px 16px; margin-bottom: 12px;">
                    <div style="font-size: 13px; color: #38BDF8; font-weight: 700; font-family: monospace;">🛰️ GPS SATELLITE BEACON</div>
                    <div style="font-size: 12.5px; color: #94A3B8; margin-top: 3px;">Click below to fetch and lock your current high-precision GPS coordinates.</div>
                </div>
                """
            )
            if st.button("🛰️ Fetch Coordinates", type="primary", use_container_width=True, key="fetch_gps_btn"):
                random_coord = random.choice(RANDOM_NYC_COORDINATES)
                st.session_state.locked_gps_xy = random_coord

                matched_name = "Auto-resolved via GPS"
                try:
                    c_parts = [float(p.strip()) for p in random_coord.split(",")]
                    for landmark, (l_lat, l_lon) in NYC_COORDINATES.items():
                        if abs(c_parts[0] - l_lat) < 0.015 and abs(c_parts[1] - l_lon) < 0.015:
                            matched_name = f"Auto-resolved via GPS ({landmark.title()})"
                            break
                except Exception:
                    pass

                st.session_state.locked_location = matched_name
                st.session_state.location_locked = True
                st.rerun()

    else:
        # Step 1 is locked! Render the locked status card and an option to unlock / edit
        render_html(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; border-radius: 6px; padding: 14px 18px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <div style="font-size: 13px; font-weight: bold; color: #34D399; font-family: monospace;">
                            🟢 LOCATION LOCKED (STEP 1 VERIFIED)
                        </div>
                        <div style="font-size: 14px; color: #F3F4F6; margin-top: 4px;">
                            <strong>Location:</strong> {html.escape(st.session_state.locked_location)}
                        </div>
                        <div style="font-size: 12.5px; color: #94A3B8; margin-top: 2px; font-family: monospace;">
                            <strong>GPS Coordinates:</strong> {html.escape(st.session_state.locked_gps_xy)}
                        </div>
                    </div>
                </div>
            </div>
            """
        )
        if st.button("🔓 Unlock / Change Location", use_container_width=False, key="unlock_loc_btn"):
            st.session_state.location_locked = False
            st.session_state.locked_location = ""
            st.session_state.locked_gps_xy = "None"
            st.rerun()

    st.markdown("---")

    # Step 2: Emergency Description & Instant Browser-side Speech-to-Text
    st.markdown("### 🚨 Step 2: Emergency Distress Transmission")

    if not st.session_state.location_locked:
        render_html(
            """
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.18); border-radius: 8px; padding: 26px; text-align: center; margin: 12px 0;">
                <div style="font-size: 15px; font-weight: bold; color: #F87171; font-family: monospace;">
                    🔒 STEP 2 LOCKED — LOCATION REQUIRED
                </div>
                <div style="font-size: 13px; color: #94A3B8; margin-top: 6px;">
                    Please complete and lock in your location in <strong>Step 1</strong> above before the emergency description area is unlocked.
                </div>
            </div>
            """
        )
        return

    # Browser-side STT Component using webkitSpeechRecognition
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }
                .stt-card {
                    background: #12161F;
                    border: 1px solid rgba(0, 128, 255, 0.3);
                    border-radius: 8px;
                    padding: 12px 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .stt-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 8px;
                }
                .stt-btn {
                    background: linear-gradient(135deg, #0080FF 0%, #0284C7 100%);
                    color: #FFFFFF;
                    border: 1px solid #38BDF8;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 700;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    box-shadow: 0 0 12px rgba(0,128,255,0.35);
                    transition: all 0.2s ease;
                }
                .stt-btn:hover {
                    box-shadow: 0 0 18px rgba(0,128,255,0.6);
                    transform: translateY(-1px);
                }
                .stt-btn.recording {
                    background: linear-gradient(135deg, #E62429 0%, #B91C1C 100%) !important;
                    border-color: #FF4D4D !important;
                    box-shadow: 0 0 20px rgba(230, 36, 41, 0.7) !important;
                    animation: pulse-mic 1.5s infinite ease-in-out;
                }
                @keyframes pulse-mic {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.03); }
                }
                .status-chip {
                    font-family: monospace;
                    font-size: 11px;
                    color: #94A3B8;
                    letter-spacing: 0.5px;
                }
                .transcript-live {
                    min-height: 44px;
                    max-height: 80px;
                    overflow-y: auto;
                    background: #0B0D12;
                    border: 1px dashed rgba(255,255,255,0.15);
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    color: #E2E8F0;
                    line-height: 1.45;
                }
                .copy-btn {
                    background: rgba(255,255,255,0.06);
                    color: #94A3B8;
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 5px;
                    padding: 6px 12px;
                    font-size: 11px;
                    font-family: monospace;
                    cursor: pointer;
                    display: none;
                }
                .copy-btn:hover {
                    color: #38BDF8;
                    border-color: #0080FF;
                }
            </style>
        </head>
        <body>
            <div class="stt-card">
                <div class="stt-header">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <button id="mic-btn" class="stt-btn" onclick="toggleDictation()">
                            <span id="mic-icon">🎙️</span>
                            <span id="mic-label">TAP TO DICTATE HANDS-FREE</span>
                        </button>
                        <span id="status-chip" class="status-chip">READY (WEB SPEECH API)</span>
                    </div>
                    <button id="copy-btn" class="copy-btn" onclick="injectIntoParent()">
                        📋 INSERT INTO MESSAGE
                    </button>
                </div>
                <div id="transcript-box" class="transcript-live">
                    Speak into your microphone. Words are transcribed instantly in your browser and synced with the text area below.
                </div>
            </div>

            <script>
                let recognition = null;
                let isListening = false;
                let currentText = '';

                const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

                if (SpeechAPI) {
                    recognition = new SpeechAPI();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';

                    recognition.onstart = function() {
                        isListening = true;
                        const btn = document.getElementById('mic-btn');
                        btn.classList.add('recording');
                        document.getElementById('mic-label').innerText = 'LISTENING... (TAP TO FINISH)';
                        document.getElementById('status-chip').innerHTML = '<span style="color: #FF4D4D; font-weight: bold;">● RECORDING AUDIO</span>';
                    };

                    recognition.onresult = function(event) {
                        let interim = '';
                        for (let i = event.resultIndex; i < event.results.length; ++i) {
                            if (event.results[i].isFinal) {
                                currentText += (currentText ? ' ' : '') + event.results[i][0].transcript.trim();
                            } else {
                                interim += event.results[i][0].transcript;
                            }
                        }
                        const combined = currentText + (interim ? ' ' + interim : '');
                        const box = document.getElementById('transcript-box');
                        box.innerText = combined;
                        box.style.color = '#F8FAFC';
                        document.getElementById('copy-btn').style.display = 'inline-block';

                        // Sync with Streamlit parent textarea
                        injectIntoParent(combined);
                    };

                    recognition.onerror = function(event) {
                        document.getElementById('status-chip').innerText = 'STATUS: ' + event.error;
                        stopDictation();
                    };

                    recognition.onend = function() {
                        stopDictation();
                    };
                } else {
                    document.getElementById('mic-btn').disabled = true;
                    document.getElementById('status-chip').innerText = 'VOICE UNSUPPORTED (TYPE BELOW)';
                }

                function toggleDictation() {
                    if (!recognition) return;
                    if (!isListening) {
                        try {
                            recognition.start();
                        } catch(e) {
                            recognition.stop();
                        }
                    } else {
                        recognition.stop();
                    }
                }

                function stopDictation() {
                    isListening = false;
                    const btn = document.getElementById('mic-btn');
                    btn.classList.remove('recording');
                    document.getElementById('mic-label').innerText = 'TAP TO DICTATE HANDS-FREE';
                    document.getElementById('status-chip').innerText = 'IDLE';
                }

                function injectIntoParent(textToInject) {
                    const text = textToInject || currentText;
                    if (!text) return;
                    try {
                        const parentDoc = window.parent.document;
                        const textarea = parentDoc.querySelector('textarea');
                        if (textarea) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                            nativeSetter.call(textarea, text);
                            textarea.dispatchEvent(new Event('input', { bubbles: true }));
                            textarea.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    } catch(err) {
                        // Cross-frame fallback if sandboxed
                    }
                }
            </script>
        </body>
        </html>
        """,
        height=125,
        scrolling=False,
    )

    # Massive Text Area for Emergency Description
    user_message = st.text_area(
        "Emergency Description (Massive Input)",
        value=st.session_state.citizen_text,
        placeholder="DESCRIBE THE SITUATION IN DETAIL (e.g., Severe gas explosion near Queens Blvd, multiple injured civilians trapped under collapsed structure, heavy smoke spreading rapidly)...",
        height=180,
        label_visibility="collapsed",
    )

    render_html("<div style='height: 8px;'></div>")

    # Primary Broadcast Action Button
    if st.button("🚨 TRANSMIT EMERGENCY DISTRESS SIGNAL", type="primary", use_container_width=True, key="submit_distress_btn"):
        if not user_message.strip():
            st.error("Please provide an emergency description or dictate using the microphone.")
        else:
            lat_val = None
            lon_val = None
            if st.session_state.locked_gps_xy and st.session_state.locked_gps_xy != "None":
                try:
                    c_parts = [float(p.strip()) for p in st.session_state.locked_gps_xy.split(",")]
                    if len(c_parts) == 2:
                        lat_val, lon_val = c_parts[0], c_parts[1]
                except Exception:
                    pass

            payload = {
                "gps_xy": st.session_state.locked_gps_xy,
                "location": st.session_state.locked_location,
                "latitude": lat_val,
                "longitude": lon_val,
                "text": user_message.strip(),
            }

            try:
                res = requests.post(INGEST_URL, json=payload, timeout=5)
                if res.status_code in [200, 201]:
                    report_data = res.json()
                    st.session_state.last_distress_report = report_data

                    # Clear session state to reset the form as requested
                    st.session_state.location_locked = False
                    st.session_state.locked_location = ""
                    st.session_state.locked_gps_xy = "None"
                    st.session_state.citizen_text = ""
                    st.rerun()
                else:
                    st.error(f"Transmission failed: {res.status_code} {res.text}")
            except Exception as e:
                # Direct in-process fallback (for Streamlit Cloud or standalone)
                try:
                    from backend import ingest_report, IngestReportPayload
                    p_obj = IngestReportPayload(**payload)
                    rep_res = ingest_report(p_obj)
                    st.session_state.last_distress_report = rep_res.model_dump()
                    st.session_state.location_locked = False
                    st.session_state.locked_location = ""
                    st.session_state.locked_gps_xy = "None"
                    st.session_state.citizen_text = ""
                    st.rerun()
                except Exception as ex:
                    st.error(f"SpidyCAD Comms Offline: ({ex})")

    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 36px; padding: 18px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 13px; color: #94A3B8; letter-spacing: 1.2px; display: flex; align-items: center; justify-content: center; gap: 10px;">
            <img src="{icon_b64}" style="width: 24px; height: 24px; border-radius: 6px; vertical-align: middle; object-fit: contain;" alt="SpidyCAD" />
            <span>🕸️ Engineered by <strong style="color: #38BDF8;">Team AlgoRhythm</strong> &nbsp;|&nbsp; SpidyCAD Citizen Emergency Dispatch</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 7. VIEW 3: DISPATCHER LOGIN (Sleek Centered Gatekeeper)
# -----------------------------------------------------------------------------
def render_dispatcher_login() -> None:
    """Render a sleek, centered Stark security terminal requiring the password KAREN-2026."""
    col_l, col_center, col_r = st.columns([1, 1.4, 1])

    with col_center:
        icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
        render_html(
            f"""
            <div style="text-align: center; margin-top: 15px; margin-bottom: 12px;">
                <img src="{icon_b64}" style="width: 95px; height: 95px; border-radius: 22px; border: 2px solid rgba(255, 51, 75, 0.85); box-shadow: 0 0 35px rgba(255, 51, 75, 0.5), 0 0 50px rgba(56, 189, 248, 0.25); background: #070b14; object-fit: contain;" alt="SpidyCAD Security" />
            </div>
            <div style="background: #12161F; border: 1px solid rgba(0, 128, 255, 0.3); border-radius: 12px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.6); position: relative;">
                <div style="font-family: monospace; font-size: 11px; color: #0080FF; letter-spacing: 1.5px; font-weight: 800;">
                    STARK SECURITY SUBSYSTEM // TERMINAL 42
                </div>
                <h2 style="font-size: 22px; font-weight: 800; color: #FFFFFF; margin: 6px 0 4px 0;">
                    🛡️ Dispatcher Terminal Login
                </h2>
                <p style="font-size: 13px; color: #94A3B8; margin: 0 0 16px 0; line-height: 1.45;">
                    Enter the Stark security clearance code to unlock the citywide radar grid, live distress queues, and unit deployment controls.
                </p>
            </div>
            """
        )

        render_html("<div style='height: 12px;'></div>")

        with st.form("dispatcher_auth_form", border=False):
            pwd = st.text_input(
                "Authorization Key",
                type="password",
                placeholder="ENTER AUTHORIZATION CODE...",
                key="login_password_field",
                label_visibility="collapsed",
            )
            sub_col, cancel_col = st.columns([1.2, 1])
            with sub_col:
                submitted = st.form_submit_button("🔓 VERIFY & UNLOCK", type="primary", use_container_width=True)
                if submitted:
                    if pwd.strip() == "KAREN-2026":
                        st.session_state.authenticated = True
                        st.session_state.auth_error = False
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.session_state.auth_error = True
                        st.rerun()
            with cancel_col:
                # Cancel button to return home
                pass

        if st.button("← ABORT / RETURN TO HOME", use_container_width=True, key="login_cancel_btn"):
            st.session_state.page = "landing"
            st.session_state.auth_error = False
            st.rerun()

        if st.session_state.auth_error:
            render_html(
                """
                <div style="background: rgba(230, 36, 41, 0.15); border: 1px solid #E62429; border-radius: 8px; padding: 14px 18px; margin-top: 16px; box-shadow: 0 0 20px rgba(230, 36, 41, 0.3);">
                    <div style="color: #FF4D4D; font-family: monospace; font-size: 13.5px; font-weight: 900; letter-spacing: 1px;">
                        ⛔ ACCESS DENIED: Unauthorized web-slinger.
                    </div>
                    <div style="color: #F8FAFC; font-size: 12px; margin-top: 4px;">
                        Security clearance violation. Password incorrect. Access restricted to authorized personnel.
                    </div>
                </div>
                """
            )


# -----------------------------------------------------------------------------
# 8. VIEW 4: DISPATCHER DASHBOARD (Stark Tactical Authority Feed)
# -----------------------------------------------------------------------------
def render_dispatcher_dashboard() -> None:
    """Render the full Authority Tactical HUD with Pydeck radar map and live prioritized queue."""
    # Ensure authentication guard
    if not st.session_state.authenticated:
        st.session_state.page = "login"
        st.rerun()
        return

    # Auto-refresh Logic (Interval: 3000 ms)
    st_autorefresh(interval=3000, limit=None, key="karen_authority_autorefresh")

    # Header Bar with SpidyCAD Icon, 'Return to Home' and Logout Actions
    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    render_html(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; background: #0A0F1E; border: 1px solid rgba(230, 36, 41, 0.35); border-radius: 12px; padding: 16px 22px; margin-bottom: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.6); flex-wrap: wrap; gap: 14px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <img src="{icon_b64}" style="width: 58px; height: 58px; border-radius: 12px; border: 1.5px solid rgba(255, 51, 75, 0.85); box-shadow: 0 0 20px rgba(255, 51, 75, 0.45); background: #070b14; object-fit: contain;" alt="SpidyCAD Logo" />
                <div>
                    <div style="margin-bottom: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span class="badge-critical mono-font">TACTICAL OPTICS ACTIVE</span>
                        <span class="badge-tech mono-font">3.0s LIVE SYNC</span>
                    </div>
                    <h1 style="font-size: 24px; font-weight: 900; color: #FFFFFF; margin: 0; line-height: 1.2;">
                        Spidy<span style="color: #FF334B;">CAD</span> Dispatch Feed // Spider-Net Triage
                    </h1>
                    <div style="font-size: 12.5px; color: #94A3B8; margin-top: 3px;">
                        Real-Time Citywide Incident Intercept • Priority-Ranked Response Protocols
                    </div>
                </div>
            </div>
            <div style="text-align: right;" class="mono-font">
                <span class="badge-tech">FRIENDLY NEIGHBORHOOD DISPATCH: ONLINE</span>
                <div style="font-size: 11px; color: #34D399; margin-top: 4px; font-weight: bold;">● FIRST RESPONDERS STANDING BY</div>
            </div>
        </div>
        """
    )

    col_nav1, col_nav2, _ = st.columns([1.2, 1, 3])
    with col_nav1:
        if st.button("🏠 Return to Home", use_container_width=True, key="dash_home_btn"):
            st.session_state.page = "landing"
            st.rerun()
    with col_nav2:
        if st.button("🔒 Log Out", use_container_width=True, key="dash_logout_btn"):
            st.session_state.authenticated = False
            st.session_state.page = "landing"
            st.rerun()

    # Fetch Data from Backend with Robust Error Handling
    reports_list = []
    backend_error = None

    try:
        r = requests.get(REPORTS_URL, timeout=3)
        if r.status_code == 200:
            reports_list = r.json()
        else:
            backend_error = f"Backend returned status {r.status_code}"
    except Exception as e:
        # Fall back to in-memory REPORTS_DB directly from backend.py
        try:
            from backend import REPORTS_DB
            reports_list = [rep.model_dump() for rep in REPORTS_DB]
            backend_error = None
        except Exception:
            try:
                import json
                p_out = WORKSPACE_ROOT / "data" / "priority_output.json"
                if p_out.exists():
                    reports_list = json.loads(p_out.read_text())[:35]
                    backend_error = None
            except Exception:
                backend_error = str(e)

    if backend_error:
        render_html(
            f"""
            <div style="background: rgba(230, 36, 41, 0.15); border: 1px solid #E62429; border-radius: 6px; padding: 14px; margin: 15px 0;">
                <div style="font-size: 13px; font-weight: bold; color: #FF4D4D; font-family: monospace;">⚠️ SPIDYCAD COMMS OFFLINE</div>
                <div style="font-size: 12px; color: #F3F4F6; margin-top: 2px;">Ensure FastAPI backend is running on :8000 (`uvicorn src.api.main:app --host 127.0.0.1 --port 8000`). Details: {html.escape(backend_error)}</div>
            </div>
            """
        )
    else:
        # Top HUD Metrics Row with Null-Safe Computation
        total_incidents = len(reports_list)
        critical_p1 = sum(
            1
            for rep in reports_list
            if safe_float(rep.get("priority")) >= 0.85
            or safe_str(rep.get("severity")).lower() == "critical"
        )
        avg_priority = (
            (sum(safe_float(rep.get("priority")) for rep in reports_list) / total_incidents * 100)
            if total_incidents > 0
            else 0.0
        )

        render_html("<div style='margin-top: 10px;'></div>")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active Incidents", f"{total_incidents} Reports")
        m2.metric(
            "Critical P1 Hazards",
            f"{critical_p1}",
            delta="Spider-Sense Alert" if critical_p1 > 0 else None,
            delta_color="inverse",
        )
        m3.metric("Average Triage Priority", f"{avg_priority:.1f}%")
        m4.metric("Stark Sentinel Status", "SCANNING NYC", delta="Online")

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Tactical Manhattan Radar Grid (Pydeck Dark Carto)
        # ---------------------------------------------------------------------
        st.markdown("### 📍 Tactical Manhattan Radar Grid")

        map_data = []
        seen_coords = {}

        for rep in reports_list:
            loc = safe_str(rep.get("location"))
            lat_raw = rep.get("latitude")
            lon_raw = rep.get("longitude")
            prio = safe_float(rep.get("priority"), 0.5)

            clean_text = safe_str(rep.get("text")).replace("\n", " ").replace('"', "'")
            rep_id = safe_str(rep.get("report_id"), "R000")
            prio_pct = f"{int(round(prio * 100))}%"

            # Coordinate inference and fallback resolution
            lat = safe_float(lat_raw, default=0.0)
            lon = safe_float(lon_raw, default=0.0)

            # Check if gps_xy string contains coordinates
            if (lat == 0.0 or lon == 0.0) and rep.get("gps_xy"):
                try:
                    c_parts = [float(p.strip()) for p in str(rep.get("gps_xy")).split(",")]
                    if len(c_parts) == 2:
                        lat, lon = c_parts[0], c_parts[1]
                except Exception:
                    pass

            if lat == 0.0 or lon == 0.0:
                matched = False
                for landmark, coords in NYC_COORDINATES.items():
                    if landmark.lower() in loc.lower() or landmark.lower() in clean_text.lower():
                        lat, lon = coords
                        matched = True
                        break
                if not matched:
                    lat, lon = 40.7580, -73.9855

            # Deterministic micro-jitter to prevent pins at the exact same location from overlapping
            coord_key = f"{lat:.4f},{lon:.4f}"
            offset_idx = seen_coords.get(coord_key, 0)
            seen_coords[coord_key] = offset_idx + 1

            if offset_idx > 0:
                step = 0.0012 * ((offset_idx + 1) // 2)
                angle_sign = 1 if offset_idx % 2 == 1 else -1
                lat += step * angle_sign
                lon += step * 0.7 * (1 if (offset_idx // 2) % 2 == 1 else -1)

            # Color palette and radii based on priority
            if prio >= 0.85:
                core_color = [230, 36, 41, 255]     # Stark Crimson
                halo_color = [230, 36, 41, 50]      # Translucent pulse aura
                core_radius = 40
                halo_radius = 95
            elif prio >= 0.60:
                core_color = [245, 158, 11, 255]    # Amber Gold
                halo_color = [245, 158, 11, 40]
                core_radius = 30
                halo_radius = 70
            else:
                core_color = [0, 160, 255, 255]     # Cyan Blue
                halo_color = [0, 160, 255, 30]
                core_radius = 22
                halo_radius = 50


            map_data.append({
                "id": rep_id,
                "text": clean_text,
                "location": loc,
                "latitude": lat,
                "longitude": lon,
                "core_color": core_color,
                "halo_color": halo_color,
                "border_color": [255, 255, 255, 240],
                "core_radius": core_radius,
                "halo_radius": halo_radius,
                "label_text": f"#{rep_id}  {prio_pct}",
                "priority": prio_pct,
            })

        if map_data:
            df_map = pd.DataFrame(map_data)

            # 1. Subtle Radar Aura Ring (Halo)
            halo_layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position=["longitude", "latitude"],
                get_color="halo_color",
                get_radius="halo_radius",
                filled=True,
                stroked=True,
                get_line_color="core_color",
                line_width_min_pixels=1,
            )

            # 2. Sleek Core Pin (Sharp Tactical Blip)
            core_layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position=["longitude", "latitude"],
                get_color="core_color",
                get_radius="core_radius",
                radius_min_pixels=4,
                radius_max_pixels=8,
                pickable=True,
                filled=True,
                stroked=True,
                get_line_color="border_color",
                line_width_min_pixels=1.5,
            )

            # 3. Floating Micro-Label (#ID + Priority)
            text_layer = pdk.Layer(
                "TextLayer",
                df_map,
                get_position=["longitude", "latitude"],
                get_text="label_text",
                get_size=10,
                get_color=[240, 244, 248, 220],
                get_alignment_baseline="'bottom'",
                get_pixel_offset=[0, -9],
                font_family="'JetBrains Mono', 'SF Mono', Consolas, monospace",
            )

            view_state = pdk.ViewState(
                latitude=40.7480,
                longitude=-73.9750,
                zoom=12.4,
                pitch=30,
            )

            try:
                r_deck = pdk.Deck(
                    layers=[halo_layer, core_layer],
                    initial_view_state=view_state,
                    map_provider="carto",
                    map_style=pdk.map_styles.CARTO_DARK,
                    tooltip={"text": "#{id} [{priority}] • {location}\n{text}"},
                )
                st.pydeck_chart(r_deck, width="stretch", height=420)
            except Exception:
                st.map(df_map, latitude="latitude", longitude="longitude", size="core_radius", color="core_color")

            render_html(
                """
                <div style="font-size: 12px; color: #94A3B8; margin-top: 6px; font-family: 'Inter', sans-serif;">
                    <span style="color: #FF4D4D; font-weight: 600;">🔴 Red Pip:</span> P1 Critical Hazard (&gt;85%) &nbsp;•&nbsp; 
                    <span style="color: #FBBF24; font-weight: 600;">🟡 Amber Pip:</span> Moderate Urgency &nbsp;•&nbsp; 
                    <span style="color: #38BDF8; font-weight: 600;">🔵 Cyan Pip:</span> Routine Status &nbsp;•&nbsp; 
                    <span style="color: #64748B;">Hover on any pin to inspect triage data</span>
                </div>
                """
            )
        else:
            st.info("No active emergency incidents currently mapped.")

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Prioritized Distress Signals (Two-Column Tactical Live Queue)
        # ---------------------------------------------------------------------
        render_html(
            f"""
            <div class="live-queue-row">
                <div class="live-queue-title">
                    <span>📋</span> Prioritized Distress Signals
                </div>
                <div class="live-queue-chip">
                    <span class="live-dot"></span>
                    <span>LIVE QUEUE:</span>
                    <strong style="color: #38BDF8; font-weight: 800;">{len(reports_list)}</strong>
                    <span>SIGNALS</span>
                </div>
            </div>
            """
        )

        if not reports_list:
            st.info("No active emergency reports in queue.")
        else:
            # Render signals row-by-row in clean pairs of columns
            for i in range(0, len(reports_list), 2):
                row_cols = st.columns(2)
                for col_idx, rep_idx in enumerate([i, i + 1]):
                    if rep_idx < len(reports_list):
                        rep = reports_list[rep_idx]
                        report_id = safe_str(rep.get("report_id"), f"R{rep_idx+1:03d}")
                        text = safe_str(rep.get("text"))
                        inc_type = safe_str(rep.get("incident_type"), "unknown").upper()
                        location = safe_str(rep.get("location"), "Location Extracted via AI")
                        severity = safe_str(rep.get("severity"), "medium").upper()
                        priority = safe_float(rep.get("priority"), 0.5)
                        credibility = safe_float(rep.get("credibility"), 0.75)
                        status_raw = safe_str(rep.get("status"), "pending")
                        status_val = status_raw.upper()
                        dispatched_unit = safe_str(rep.get("dispatched_unit"), "Spider-Man / FDNY Team 1")
                        is_dispatched = status_raw.lower() == "dispatched"

                        prio_pct = f"{int(round(priority * 100))}%"
                        cred_pct = f"{int(round(credibility * 100))}%"

                        # Spider-Sense Danger Pulse for P1 Hazards (> 85%)
                        is_p1 = priority >= 0.85
                        pulse_class = "spidey-pulse-card" if is_p1 else ""

                        if priority >= 0.85:
                            badge_style = "badge-critical"
                            prio_color = "#E62429"
                        elif priority >= 0.60:
                            badge_style = "badge-warning"
                            prio_color = "#F59E0B"
                        else:
                            badge_style = "badge-routine"
                            prio_color = "#94A3B8"

                        status_badge_style = "badge-dispatched" if is_dispatched else "badge-routine"

                        # Card Component with Corner Optics & HTML Escaping
                        safe_display_text = html.escape(text)
                        safe_display_loc = html.escape(location)

                        injured_cnt = rep.get("injured_count")
                        affected_cnt = rep.get("affected_count")
                        casualty_badge = ""
                        if injured_cnt:
                            casualty_badge = f'<span class="meta-dot">•</span><span style="color: #FF4D4D; font-weight: 800; font-size: 11px;">⚠️ {injured_cnt} INJURED</span>'
                        elif affected_cnt:
                            casualty_badge = f'<span class="meta-dot">•</span><span style="color: #F59E0B; font-weight: 800; font-size: 11px;">👥 {affected_cnt} AFFECTED</span>'

                        card_html = f"""
                        <div class="karen-card {pulse_class}">
                            <div class="card-header-bar">
                                <div class="card-header-tags">
                                    <span class="badge-tech mono-font">#{html.escape(report_id)}</span>
                                    <span class="mono-font" style="font-size: 12.5px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.6px;">
                                        {html.escape(inc_type)}
                                    </span>
                                    <span class="{badge_style} mono-font">
                                        {html.escape(severity)}
                                    </span>
                                </div>
                                <div class="mono-font prio-score-wrap" style="color: {prio_color};">
                                    {prio_pct} <span style="font-size: 10px; font-weight: 700; opacity: 0.85; letter-spacing: 1px;">PRIORITY</span>
                                </div>
                            </div>

                            <div class="card-msg-text">
                                {safe_display_text}
                            </div>

                            <div class="card-footer-bar">
                                <div class="card-loc-meta">
                                    <span style="font-size: 13px;">📍</span>
                                    <span class="loc-label">{safe_display_loc}</span>
                                    <span class="meta-dot">•</span>
                                    <span class="cred-meta">Cred:</span>
                                    <span class="cred-val">{cred_pct}</span>
                                    {casualty_badge}
                                </div>
                                <div>
                                    <span class="{status_badge_style} mono-font">{status_val}</span>
                                </div>
                            </div>
                        </div>
                        """
                        with row_cols[col_idx]:
                            render_html(card_html)

                            # Quick Dispatch Action / Status Row
                            if is_dispatched:
                                render_html(
                                    f"""
                                    <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; border-radius: 6px; padding: 8px 12px; margin-bottom: 14px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #34D399; display: flex; justify-content: space-between; align-items: center;">
                                        <span>✅ UNIT ON SCENE: <strong>{html.escape(dispatched_unit)}</strong></span>
                                        <span style="color: #A7F3D0; font-size: 11px; letter-spacing: 0.5px;">EN ROUTE</span>
                                    </div>
                                    """
                                )
                            else:
                                btn_key = f"disp_{report_id}_{rep_idx}"
                                if st.button(
                                    f"🕸️ DISPATCH FIRST RESPONDERS (#{report_id})",
                                    key=btn_key,
                                    use_container_width=True,
                                ):
                                    try:
                                        patch_res = requests.patch(
                                            f"{BACKEND_URL}/api/reports/{report_id}/dispatch",
                                            json={"status": "dispatched", "dispatched_unit": "Spider-Man / FDNY Team 1"},
                                            timeout=3,
                                        )
                                        if patch_res.status_code in [200, 204]:
                                            st.success(f"First responders dispatched to #{report_id}!")
                                            st.rerun()
                                        else:
                                            st.error(f"Dispatch failed: {patch_res.status_code} {patch_res.text}")
                                    except Exception as ex:
                                        # In-memory fallback
                                        try:
                                            from backend import update_dispatch_status, DispatchUpdatePayload
                                            update_dispatch_status(report_id, DispatchUpdatePayload(status="dispatched", dispatched_unit="Spider-Man / FDNY Team 1"))
                                            st.success(f"First responders dispatched to #{report_id}!")
                                            st.rerun()
                                        except Exception as fallback_ex:
                                            st.error(f"Dispatch update failed: {fallback_ex}")

    icon_b64 = get_image_base64("spidycad-logo.svg") or get_image_base64("spidycad-logo.png")
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 40px; padding: 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 13px; color: #94A3B8; letter-spacing: 1.2px; display: flex; align-items: center; justify-content: center; gap: 10px;">
            <img src="{icon_b64}" style="width: 24px; height: 24px; border-radius: 6px; vertical-align: middle; object-fit: contain;" alt="SpidyCAD" />
            <span>🕸️ Engineered by <strong style="color: #38BDF8;">Team AlgoRhythm</strong> &nbsp;|&nbsp; SpidyCAD Computer-Aided Dispatch</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 9. Main Router Switch
# -----------------------------------------------------------------------------
render_top_navigation_bar()

if st.session_state.page == "landing":
    render_landing_page()
elif st.session_state.page == "citizen":
    render_citizen_portal()
elif st.session_state.page == "login":
    render_dispatcher_login()
elif st.session_state.page == "dashboard":
    render_dispatcher_dashboard()
else:
    st.session_state.page = "landing"
    st.rerun()
