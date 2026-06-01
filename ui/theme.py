"""theme.py - Background via Streamlit static serving from ui/static/"""
import streamlit as st, shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# theme.py lives in ui/ — so ROOT is ui/ and static is ui/static/
UI_DIR   = Path(__file__).resolve().parent
ROOT_DIR = UI_DIR.parent
STATIC   = UI_DIR / "static"

def get_time_of_day():
    IST = timezone(timedelta(hours=5, minutes=30))
    h = datetime.now(IST).hour
    if 5 <= h < 12:   return "morning"
    elif 12 <= h < 17: return "afternoon"
    elif 17 <= h < 21: return "evening"
    else:              return "night"

TIME_META = {
    "morning":   {"mood":"🌅 Good morning — a hopeful new day begins",         "title":"#FFFFFF","sub":"#FFE082","shadow":"rgba(255,200,0,0.8)","overlay":"rgba(0,0,0,0.22)"},
    "afternoon": {"mood":"☀️ Afternoon — resilience, hard work, companionship", "title":"#FFFFFF","sub":"#FFE082","shadow":"rgba(255,200,0,0.7)","overlay":"rgba(0,0,0,0.26)"},
    "evening":   {"mood":"🌇 Evening — dignity of labour, rest well earned",    "title":"#FFFFFF","sub":"#FFCC80","shadow":"rgba(255,140,0,0.8)","overlay":"rgba(0,0,0,0.30)"},
    "night":     {"mood":"🌙 Night — GBoy watches while the world rests",       "title":"#FFFFFF","sub":"#C5CAE9","shadow":"rgba(150,150,255,0.7)","overlay":"rgba(0,0,0,0.46)"},
}
FALLBACKS = {
    "morning":   "linear-gradient(180deg,#fff8e1 0%,#ffe082 15%,#a5d6a7 55%,#66bb6a 80%,#388e3c 100%)",
    "afternoon": "linear-gradient(180deg,#e3f2fd 0%,#b3e5fc 20%,#a5d6a7 55%,#66bb6a 80%,#388e3c 100%)",
    "evening":   "linear-gradient(180deg,#bf360c 0%,#ff8f00 25%,#ffb300 40%,#a5d6a7 65%,#388e3c 100%)",
    "night":     "linear-gradient(180deg,#0a0e27 0%,#1a237e 30%,#283593 50%,#2e7d32 75%,#1b5e20 100%)",
}

def _setup_static():
    """Copy background images from assets/ into ui/static/ automatically."""
    STATIC.mkdir(parents=True, exist_ok=True)
    assets = ROOT_DIR / "assets"
    if not assets.exists():
        return
    for tod in ["morning","afternoon","evening","night"]:
        for ext in ["jpg","jpeg","png"]:
            src = assets / f"bg_{tod}.{ext}"
            dst = STATIC / f"bg_{tod}.{ext}"
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)

def _get_bg_url(tod):
    for ext in ["jpg","jpeg","png"]:
        src = ROOT_DIR / "assets" / f"bg_{tod}.{ext}"
        if src.exists():
            import base64
            with open(src, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:image/{ext};base64,{b64}"
    return None

_setup_static()

def apply_theme():
    tod  = get_time_of_day()
    meta = TIME_META[tod]
    tc, sc, ov, shad = meta["title"], meta["sub"], meta["overlay"], meta["shadow"]

    bg_url = _get_bg_url(tod)

    if bg_url:
        bg_css = (
            f'.stApp{{background-image:url("{bg_url}")!important;'
            'background-size:cover!important;background-position:center!important;'
            'background-attachment:fixed!important;background-repeat:no-repeat!important;}'
            f'[data-testid="stAppViewContainer"]{{background-image:url("{bg_url}")!important;'
            'background-size:cover!important;background-position:center!important;'
            'background-attachment:fixed!important;}}'
        )
        overlay = (
            '<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;'
            f'background:{ov};z-index:0;pointer-events:none;"></div>'
        )
    else:
        bg_css  = f'.stApp{{background:{FALLBACKS[tod]}!important;background-attachment:fixed!important;}}'
        overlay = ""

    st.markdown(
        '<style>'
        '@import url(\'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700;900&family=Nunito:wght@400;600;700;800&display=swap\');'
        'section[data-testid="stSidebarNav"]{display:none!important;height:0!important;overflow:hidden!important;visibility:hidden!important;min-height:0!important;max-height:0!important;}'
        'div[data-testid="stSidebarNavItems"]{display:none!important;height:0!important;overflow:hidden!important;visibility:hidden!important;}'
        'ul[data-testid="stSidebarNavItems"]{display:none!important;}'
        + bg_css +
        '[data-testid="stAppViewContainer"]>section,.main .block-container,'
        '[data-testid="stMain"],[data-testid="stBottom"]{background:transparent!important;}'
        '#MainMenu,footer,header{visibility:hidden;}'
        '.block-container{padding-top:0.8rem!important;position:relative;z-index:1;max-width:1200px;}'
        f'.page-title{{font-family:\'Cormorant Garamond\',serif!important;font-size:2.4rem;font-weight:900;color:{tc};text-shadow:0 2px 4px rgba(0,0,0,0.95),0 0 20px {shad};margin-bottom:0.15rem;line-height:1.1;letter-spacing:0.02em;}}'
        f'.page-sub{{font-size:0.92rem;font-weight:700;color:{sc};text-shadow:0 1px 4px rgba(0,0,0,0.95);margin-bottom:0.8rem;}}'
        f'.mood-bar{{background:rgba(0,0,0,0.55);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.2);border-radius:30px;padding:0.3rem 1rem;display:inline-block;font-size:0.8rem;font-weight:700;color:{sc};text-shadow:0 1px 4px rgba(0,0,0,0.9);margin-bottom:0.8rem;}}'
        f'.field-card{{background:rgba(0,0,0,0.5);backdrop-filter:blur(16px);border:1.5px solid rgba(255,255,255,0.2);border-radius:18px;padding:1.2rem;box-shadow:0 8px 32px rgba(0,0,0,0.5);margin-bottom:1rem;color:{tc};}}'
        f'.nav-card{{background:rgba(0,0,0,0.5);backdrop-filter:blur(14px);border:2px solid rgba(255,255,255,0.22);border-radius:18px;padding:1.3rem 0.8rem;text-align:center;cursor:pointer;transition:all 0.3s cubic-bezier(.34,1.56,.64,1);box-shadow:0 6px 24px rgba(0,0,0,0.5);text-decoration:none;display:block;}}'
        f'.nav-card:hover{{transform:translateY(-7px) scale(1.03);background:rgba(0,0,0,0.7);box-shadow:0 16px 40px rgba(0,0,0,0.6);border-color:rgba(255,255,255,0.4);}}'
        '.nav-card:active{transform:translateY(1px);}'
        '.nav-emoji{font-size:2.4rem;display:block;margin-bottom:0.5rem;}'
        f'.nav-title{{font-family:\'Cormorant Garamond\',serif!important;font-size:1.1rem;font-weight:700;color:{tc};display:block;margin-bottom:0.2rem;text-shadow:0 1px 6px rgba(0,0,0,0.95);}}'
        f'.nav-desc{{font-size:0.75rem;color:{sc};display:block;line-height:1.4;text-shadow:0 1px 4px rgba(0,0,0,0.8);}}'
        f'.back-btn{{display:inline-flex;align-items:center;gap:0.4rem;background:rgba(0,0,0,0.55);backdrop-filter:blur(10px);border:1.5px solid rgba(255,255,255,0.25);border-radius:30px;padding:0.3rem 0.9rem;font-weight:700;font-size:0.82rem;color:{tc};text-decoration:none;text-shadow:0 1px 4px rgba(0,0,0,0.8);box-shadow:0 3px 10px rgba(0,0,0,0.4);transition:all 0.2s;margin-bottom:0.8rem;}}'
        f'.back-btn:hover{{background:rgba(0,0,0,0.75);transform:translateY(-1px);color:{tc};}}'
        '.admin-corner{position:fixed;top:12px;right:12px;z-index:9999;background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);border:1.5px solid rgba(255,255,255,0.25);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:1rem;text-decoration:none;color:rgba(255,255,255,0.9);box-shadow:0 3px 12px rgba(0,0,0,0.6);transition:all 0.2s;}'
        '.admin-corner:hover{background:rgba(0,0,0,0.8);transform:scale(1.1);}'
        f'[data-testid="stSidebar"]{{background:rgba(0,0,0,0.6)!important;backdrop-filter:blur(20px)!important;border-right:1.5px solid rgba(255,255,255,0.1)!important;}}'
        f'[data-testid="stSidebar"] *{{color:{tc}!important;}}'
        f'.stButton>button{{background:rgba(0,0,0,0.55)!important;backdrop-filter:blur(10px)!important;color:{tc}!important;border:1.5px solid rgba(255,255,255,0.3)!important;border-radius:14px!important;font-weight:700!important;box-shadow:0 4px 15px rgba(0,0,0,0.5)!important;transition:all 0.2s!important;text-shadow:0 1px 4px rgba(0,0,0,0.7)!important;}}'
        '.stButton>button:hover{background:rgba(0,0,0,0.75)!important;transform:translateY(-2px)!important;}'
        '.stButton>button:active{transform:translateY(1px)!important;}'
        '.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(0,0,0,0.5)!important;backdrop-filter:blur(10px)!important;border:1.5px solid rgba(255,255,255,0.25)!important;border-radius:12px!important;color:#FFFFFF!important;font-weight:600!important;}'
        '.stTextInput>div>div>input::placeholder{color:rgba(255,255,255,0.45)!important;}'
        '.stSelectbox>div>div{background:rgba(0,0,0,0.5)!important;backdrop-filter:blur(10px)!important;border:1.5px solid rgba(255,255,255,0.25)!important;border-radius:12px!important;color:#FFFFFF!important;}'
        '.stRadio label{color:#FFFFFF!important;font-weight:600!important;text-shadow:0 1px 4px rgba(0,0,0,0.95);}'
        '.stRadio [data-testid="stMarkdownContainer"] p{color:#FFFFFF!important;}'
        '.stExpander{background:rgba(0,0,0,0.45)!important;backdrop-filter:blur(10px);border:1.5px solid rgba(255,255,255,0.15)!important;border-radius:14px!important;}'
        '.stExpander summary,.stExpander summary p{color:#FFFFFF!important;font-weight:700!important;}'
        '[data-testid="stMetricValue"]{color:#FFFFFF!important;font-size:2.2rem!important;}'
        f'[data-testid="stMetricLabel"]{{color:{sc}!important;}}'
        'hr{border-color:rgba(255,255,255,0.12)!important;}'
        '.stSuccess{background:rgba(20,80,20,0.65)!important;border-radius:12px!important;} .stSuccess p{color:#FFFFFF!important;}'
        '.stError{background:rgba(100,20,20,0.65)!important;border-radius:12px!important;} .stError p{color:#FFFFFF!important;}'
        '.stInfo{background:rgba(20,40,100,0.65)!important;border-radius:12px!important;} .stInfo p{color:#FFFFFF!important;}'
        '.stWarning{background:rgba(100,60,0,0.65)!important;border-radius:12px!important;} .stWarning p{color:#FFFFFF!important;}'
        '.grass-strip{font-size:1.5rem;text-align:center;letter-spacing:6px;animation:grassSway 3s ease-in-out infinite alternate;margin-top:1.5rem;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.7));}'
        '@keyframes grassSway{0%{letter-spacing:4px}100%{letter-spacing:9px}}'
        '</style>'
        + overlay +
        '<a href="/gaps" class="admin-corner" title="Admin">🔒</a>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="mood-bar">{meta["mood"]}</div>', unsafe_allow_html=True)
    return tod

def sidebar_nav(current=""):
    tod = get_time_of_day()
    tc  = TIME_META[tod]["title"]
    sc  = TIME_META[tod]["sub"]
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:1.2rem 0 0.8rem;">'
            f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.4rem;font-weight:900;color:{tc};letter-spacing:0.04em;text-shadow:0 2px 8px rgba(0,0,0,0.9);">⚖️ Labour Law AI</div>'
            f'<div style="font-size:0.55rem;color:{sc};margin-top:0.2rem;font-weight:700;letter-spacing:0.06em;text-shadow:0 1px 4px rgba(0,0,0,0.8);">POWERED BY CLAUDE AI</div>'
            '</div><hr style="border:1px solid rgba(255,255,255,0.1);margin:0 0 0.8rem;">',
            unsafe_allow_html=True)
        for emoji,label,url in [("🏡","Home","/"),("📚","Knowledge Digest","/digest"),
               ("💬","Legal Q&A","/qa"),("🎯","Quiz","/quiz"),
               ("🧗","Rope Climb","/rope"),("🐕","GBoy Chat","/gboy")]:
            a  = current==label
            bg = "rgba(255,255,255,0.18)" if a else "rgba(255,255,255,0.07)"
            bd = "rgba(255,255,255,0.4)"  if a else "rgba(255,255,255,0.12)"
            st.markdown(
                f'<a href="{url}" style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0.8rem;margin-bottom:0.3rem;border-radius:12px;background:{bg};backdrop-filter:blur(8px);border:1.5px solid {bd};text-decoration:none;font-weight:700;color:{tc};font-size:0.88rem;text-shadow:0 1px 6px rgba(0,0,0,0.9);box-shadow:0 2px 8px rgba(0,0,0,0.3);transition:all 0.15s;"><span style="font-size:1.05rem;">{emoji}</span> {label}</a>',
                unsafe_allow_html=True)
        st.markdown(
            f'<div style="padding:1rem 0 0.3rem;text-align:center;font-size:0.65rem;color:{sc};opacity:0.55;letter-spacing:0.05em;">🌱 LABOUR LAW AI V2.0</div>'
            f'<div style="text-align:center;font-size:0.75rem;color:{sc};opacity:0.7;letter-spacing:0.04em;font-weight:600;">Created by CA Karan Panjwani</div>',
            unsafe_allow_html=True)

def back_button():
    st.markdown('<a href="/" class="back-btn">← Back to Dashboard</a>', unsafe_allow_html=True)
