"""page_home.py — Dashboard — Admin gap detector hidden"""
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from theme import apply_theme, sidebar_nav

st.set_page_config(page_title="Labour Law AI", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
apply_theme()
sidebar_nav("Home")

st.markdown("""
<style>
.hero-title {
    font-family:'Playfair Display',serif; font-size:3.2rem; font-weight:900;
    color:#1b5e20; text-align:center; line-height:1.1;
    text-shadow:2px 3px 0 rgba(255,255,255,0.5), 0 0 40px rgba(255,179,0,0.2);
    margin-bottom:0.3rem;
}
.hero-sub {
    text-align:center; font-size:1.05rem; color:#2e7d32;
    font-weight:600; margin-bottom:2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">⚖️ Labour Law AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">🌿 Your peaceful guide through the field of Indian Labour Law 🌿</div>', unsafe_allow_html=True)

# 4 cards — NO Gap Detector (admin only)
col1, col2, col3, col4 = st.columns(4)

cards = [
    (col1, "📚", "Knowledge Digest", "Browse Acts, Rules & Judgments in plain language", "/digest"),
    (col2, "💬", "Legal Q&A",        "Ask any labour law question instantly",             "/qa"),
    (col3, "🎯", "Quiz",             "Test your knowledge with topic-based questions",    "/quiz"),
    (col4, "🧗", "Rope Climb",       "Score 5/10 to reach the top!",                     "/rope"),
]

for col, emoji, title, desc, url in cards:
    with col:
        st.markdown(f"""
        <a href="{url}" class="nav-card">
            <span class="nav-emoji">{emoji}</span>
            <span class="nav-title">{title}</span>
            <span class="nav-desc">{desc}</span>
        </a>
        """, unsafe_allow_html=True)

st.write("")
st.divider()

# GBoy section
col_a, col_b, col_c = st.columns([1,2,1])
with col_b:
    # Load avatar
    avatar_path = Path(__file__).parent.parent / "assets" / "gboy.png"
    if avatar_path.exists():
        import base64
        with open(avatar_path,"rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_src = f"data:image/png;base64,{img_b64}"
    else:
        img_src = "https://api.dicebear.com/7.x/bottts/svg?seed=gboy&backgroundColor=c8e6c9"

    st.markdown(f"""
    <div style="text-align:center;">
        <img src="{img_src}" style="
            width:200px; height:200px; border-radius:50%; object-fit:cover;
            border:5px solid rgba(255,255,255,0.7);
            box-shadow:0 10px 40px rgba(56,142,60,0.35), 0 0 0 10px rgba(255,255,255,0.2);
            cursor:pointer; transition:all 0.4s cubic-bezier(.34,1.56,.64,1);
            animation:gboyFloat 3s ease-in-out infinite;
        "
        onmouseover="this.style.transform='scale(1.12) rotate(-4deg)'; this.style.boxShadow='0 20px 50px rgba(56,142,60,0.5), 0 0 0 14px rgba(255,255,255,0.25)';"
        onmouseout="this.style.transform='scale(1) rotate(0deg)'; this.style.boxShadow='0 10px 40px rgba(56,142,60,0.35), 0 0 0 10px rgba(255,255,255,0.2)';"
        title="Click to chat with GBoy!"
        onclick="window.location='/gboy'"
        />
        <style>
        @keyframes gboyFloat {{
            0%,100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        </style>
        <div style="margin-top:0.8rem;">
            <div style="font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:900; color:#1b5e20;">
                🐕 Meet GBoy
            </div>
            <div style="font-size:0.85rem; color:#558b2f; font-weight:600; margin:0.3rem 0;">
                Your Labour Law AI Superhero — hover over me for a hint!
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🐾 Chat with GBoy →", use_container_width=True):
        st.switch_page("pages/gboy.py")

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱🌾🌿🍃</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:0.72rem; color:rgba(27,94,32,0.6); margin-top:0.8rem; font-family:Nunito,sans-serif;">Labour Law AI — Powered by Claude AI (Anthropic) | Built for the working people of India</div>', unsafe_allow_html=True)
