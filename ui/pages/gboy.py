"""
gboy.py — GBoy with sleeping/waking animation states
- Sleeping image shown before wake up
- Breathing animation while sleeping
- Transition to awake image when woken
- Returns to sleeping image when put to sleep
"""
import streamlit as st, anthropic, os, sys, base64
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, sidebar_nav, back_button, get_time_of_day, TIME_META
load_dotenv()

st.set_page_config(page_title="GBoy Chat", page_icon="🐕", layout="centered")
apply_theme()
sidebar_nav("GBoy Chat")
back_button()

api_key = os.getenv("ANTHROPIC_API_KEY","")
tod     = get_time_of_day()
tc      = TIME_META[tod]["title"]
sc      = TIME_META[tod]["sub"]

FREE_LIMIT = int(os.getenv("FREE_QUERY_LIMIT", "2"))
if "gboy_query_count" not in st.session_state: st.session_state.gboy_query_count = 0
if "user_api_key"     not in st.session_state: st.session_state.user_api_key     = ""

# ── Load both images ─────────────────────────────────────────
def load_img(filename):
    path = Path(__file__).parents[2] / "assets" / filename
    if path.exists():
        with open(path,"rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext  = path.suffix.lstrip(".")
        mime = "jpeg" if ext in ("jpg","jpeg") else "png"
        return f"data:image/{mime};base64,{b64}"
    return None

img_awake = load_img("gboy.png")
img_sleep = load_img("gboy_sleep.png")

if not img_awake:
    img_awake = "https://api.dicebear.com/7.x/bottts/svg?seed=gboy-awake&size=240"
if not img_sleep:
    img_sleep = "https://api.dicebear.com/7.x/bottts/svg?seed=gboy-sleep&size=240&mood=sad"

st.markdown(f"""
<style>
.block-container {{ max-width:720px !important; padding-left:1rem !important; padding-right:1rem !important; }}
.paw-field {{ position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }}
.paw {{ position:absolute; font-size:1rem; opacity:0; animation:pawFloat 4s ease-in-out infinite; }}
.paw:nth-child(1){{ left:8%;  bottom:20%; animation-delay:0s;   animation-duration:4.5s; }}
.paw:nth-child(2){{ left:20%; bottom:10%; animation-delay:1.2s; animation-duration:5s; }}
.paw:nth-child(3){{ left:75%; bottom:25%; animation-delay:0.6s; animation-duration:4s; }}
.paw:nth-child(4){{ left:88%; bottom:15%; animation-delay:2s;   animation-duration:5.5s; }}
.paw:nth-child(5){{ left:50%; bottom:5%;  animation-delay:1.8s; animation-duration:4.2s; }}
.paw:nth-child(6){{ left:35%; bottom:30%; animation-delay:3s;   animation-duration:3.8s; }}
@keyframes pawFloat {{
    0%   {{ opacity:0;   transform:translateY(0)   rotate(0deg)   scale(0.5); }}
    15%  {{ opacity:0.6; }}
    85%  {{ opacity:0.3; }}
    100% {{ opacity:0;   transform:translateY(-160px) rotate(25deg) scale(1.1); }}
}}
.gboy-center {{ display:flex; flex-direction:column; align-items:center; padding:1.5rem 0 0.5rem; }}
@keyframes breathe {{
    0%,100% {{ transform:scale(1) translateY(0); filter:brightness(0.95); }}
    40%     {{ transform:scale(1.03) translateY(-4px); filter:brightness(1.05); }}
    60%     {{ transform:scale(1.02) translateY(-3px); }}
}}
@keyframes zFloat {{
    0%   {{ opacity:0; transform:translate(0,0) scale(0.5); }}
    30%  {{ opacity:1; }}
    100% {{ opacity:0; transform:translate(20px,-40px) scale(1.2); }}
}}
.gboy-sleeping {{
    width:240px; height:240px; object-fit:contain; border-radius:50%;
    border:5px solid rgba(255,255,255,0.3);
    box-shadow:0 12px 40px rgba(0,0,0,0.5), 0 0 0 10px rgba(255,255,255,0.08);
    animation:breathe 3.5s ease-in-out infinite;
    display:block; background:rgba(0,0,0,0.2);
}}
.z-wrap {{ position:relative; display:inline-block; }}
.z1,.z2,.z3 {{
    position:absolute; font-weight:900; color:rgba(255,255,255,0.7);
    font-family:'Cormorant Garamond',serif; text-shadow:0 2px 8px rgba(0,0,0,0.5);
    animation:zFloat 3s ease-in-out infinite; pointer-events:none;
}}
.z1 {{ font-size:1.4rem; top:-10px; right:-5px;  animation-delay:0s; }}
.z2 {{ font-size:1.0rem; top:-30px; right:-20px; animation-delay:1s; }}
.z3 {{ font-size:0.7rem; top:-45px; right:-35px; animation-delay:2s; }}
@keyframes wakeShake {{
    0%  {{ transform:rotate(0deg) scale(1); }}
    15% {{ transform:rotate(-8deg) scale(0.95); }}
    30% {{ transform:rotate(8deg) scale(1.05); }}
    45% {{ transform:rotate(-5deg) scale(0.98); }}
    60% {{ transform:rotate(5deg) scale(1.08); }}
    75% {{ transform:rotate(-2deg) scale(1.04); }}
    100%{{ transform:rotate(0deg) scale(1); }}
}}
.gboy-waking {{
    width:240px; height:240px; object-fit:contain; border-radius:50%;
    border:5px solid rgba(255,200,0,0.6);
    box-shadow:0 0 40px rgba(255,200,0,0.4), 0 12px 40px rgba(0,0,0,0.5);
    animation:wakeShake 0.8s ease-in-out 1; display:block; background:rgba(0,0,0,0.2);
}}
@keyframes gboyFloat {{
    0%,100% {{ transform:translateY(0) rotate(0deg); }}
    33%     {{ transform:translateY(-10px) rotate(-1.5deg); }}
    66%     {{ transform:translateY(-5px)  rotate(1.5deg); }}
}}
@keyframes gboyExcited {{
    0%,100% {{ transform:scale(1) rotate(0deg); }}
    20% {{ transform:scale(1.1) rotate(-5deg); }}
    40% {{ transform:scale(1.14) rotate(4deg); }}
    60% {{ transform:scale(1.08) rotate(-3deg); }}
    80% {{ transform:scale(1.05) rotate(2deg); }}
}}
@keyframes haloPulse {{
    0%,100% {{ opacity:0.4; transform:scale(1) rotate(0deg); }}
    50%     {{ opacity:0.85; transform:scale(1.04) rotate(180deg); }}
}}
@keyframes haloSpin {{ from{{ transform:rotate(0deg); }} to{{ transform:rotate(360deg); }} }}
.avatar-ring {{
    width:240px; height:240px; border-radius:50%; position:relative;
    cursor:pointer; flex-shrink:0; filter:drop-shadow(0 12px 30px rgba(0,0,0,0.5));
}}
.avatar-ring::before {{
    content:''; position:absolute; inset:-8px; border-radius:50%;
    border:3px solid rgba(255,255,255,0.5);
    animation:haloPulse 3s ease-in-out infinite; pointer-events:none;
}}
.avatar-ring::after {{
    content:''; position:absolute; inset:-14px; border-radius:50%;
    border:2px dashed rgba(255,255,255,0.25);
    animation:haloSpin 8s linear infinite; pointer-events:none;
}}
.avatar-img {{
    width:240px; height:240px; object-fit:contain; border-radius:50%;
    border:5px solid rgba(255,255,255,0.75);
    animation:gboyFloat 4s ease-in-out infinite;
    display:block; background:rgba(0,0,0,0.2);
}}
.avatar-ring:hover .avatar-img {{ animation:gboyExcited 0.5s ease-in-out infinite !important; }}
.avatar-tooltip {{
    position:absolute; top:-42px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.65); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.25); border-radius:20px;
    padding:0.28rem 0.75rem; font-size:0.75rem; white-space:nowrap;
    color:rgba(255,255,255,0.9); font-family:'Nunito',sans-serif; font-weight:700;
    opacity:0; transition:opacity 0.2s; pointer-events:none; letter-spacing:0.03em;
}}
.avatar-ring:hover .avatar-tooltip {{ opacity:1; }}
@keyframes goSleep {{
    0%  {{ transform:scale(1) rotate(0deg); filter:brightness(1); }}
    30% {{ transform:scale(0.95) rotate(5deg); filter:brightness(0.8); }}
    60% {{ transform:scale(0.98) rotate(-3deg); filter:brightness(0.6); }}
    100%{{ transform:scale(1) rotate(0deg); filter:brightness(0.9); }}
}}
.gboy-goingsleep {{
    width:240px; height:240px; object-fit:contain; border-radius:50%;
    border:5px solid rgba(255,255,255,0.2);
    animation:goSleep 1.2s ease-in-out 1 forwards;
    display:block; background:rgba(0,0,0,0.2);
}}
.gboy-name {{
    font-family:'Cormorant Garamond',serif !important;
    font-size:2.2rem; font-weight:900; letter-spacing:0.05em;
    color:{tc}; margin-top:1rem; text-shadow:0 2px 20px rgba(0,0,0,0.6); text-align:center;
}}
.gboy-tag {{
    font-family:'Nunito',sans-serif; font-size:0.78rem; font-weight:800;
    color:{sc}; letter-spacing:0.12em; text-transform:uppercase;
    text-shadow:0 1px 8px rgba(0,0,0,0.5); text-align:center; margin-top:0.25rem;
}}
.status-badge {{
    display:inline-flex; align-items:center; gap:0.3rem;
    background:rgba(0,0,0,0.3); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,0.2); border-radius:30px;
    padding:0.2rem 0.7rem; font-size:0.72rem; font-weight:700;
    font-family:'Nunito',sans-serif; letter-spacing:0.05em;
    color:{sc}; margin-top:0.5rem; text-shadow:0 1px 4px rgba(0,0,0,0.4);
}}
.status-dot {{ width:7px; height:7px; border-radius:50%; animation:dotPulse 1.5s ease-in-out infinite; }}
@keyframes dotPulse {{ 0%,100%{{opacity:.5;transform:scale(1)}} 50%{{opacity:1;transform:scale(1.3)}} }}
.speech-bubble {{
    background:rgba(255,255,255,0.1); backdrop-filter:blur(14px);
    border:1.5px solid rgba(255,255,255,0.25); border-radius:0 20px 20px 20px;
    padding:0.9rem 1.2rem; margin:0.8rem 0;
    color:{tc}; font-family:'Nunito',sans-serif; font-size:0.9rem; line-height:1.65;
    text-shadow:0 1px 4px rgba(0,0,0,0.35); width:100%; box-shadow:0 4px 24px rgba(0,0,0,0.2);
}}
.hint-box {{
    background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
    border:2px dashed rgba(255,255,255,0.2); border-radius:16px;
    padding:1rem 1.2rem; text-align:center; width:100%;
    color:{sc}; font-family:'Nunito',sans-serif; font-size:0.9rem; font-weight:600;
    text-shadow:0 1px 6px rgba(0,0,0,0.4); animation:hintPulse 2.5s ease-in-out infinite;
}}
@keyframes hintPulse {{ 0%,100%{{opacity:0.7}} 50%{{opacity:1}} }}
.sleep-note {{
    background:rgba(0,0,0,0.25); backdrop-filter:blur(10px);
    border:1.5px solid rgba(255,255,255,0.15); border-radius:16px;
    padding:0.8rem 1.2rem; text-align:center; width:100%; margin-top:0.8rem;
    color:{sc}; font-family:'Nunito',sans-serif; font-size:0.85rem; font-weight:600;
    text-shadow:0 1px 4px rgba(0,0,0,0.4);
}}
.chat-area {{ display:flex; flex-direction:column; gap:0.6rem; margin:0.8rem 0; width:100%; }}
.msg-user {{ display:flex; justify-content:flex-end; width:100%; }}
.msg-bot  {{ display:flex; justify-content:flex-start; width:100%; }}
.bub-user {{
    background:rgba(255,255,255,0.18); backdrop-filter:blur(8px);
    border:1.5px solid rgba(255,255,255,0.3); border-radius:18px 18px 4px 18px;
    padding:0.55rem 0.9rem; max-width:80%;
    color:{tc}; font-family:'Nunito',sans-serif; font-size:0.88rem;
    text-shadow:0 1px 3px rgba(0,0,0,0.35); line-height:1.5;
}}
.bub-bot {{
    background:rgba(0,0,0,0.22); backdrop-filter:blur(8px);
    border:1.5px solid rgba(255,255,255,0.18); border-radius:4px 18px 18px 18px;
    padding:0.55rem 0.9rem; max-width:80%;
    color:{tc}; font-family:'Nunito',sans-serif; font-size:0.88rem;
    text-shadow:0 1px 3px rgba(0,0,0,0.35); line-height:1.5;
}}
.bub-label {{
    font-size:0.65rem; color:{sc}; font-weight:800; letter-spacing:0.06em;
    font-family:'Nunito',sans-serif; text-shadow:0 1px 4px rgba(0,0,0,0.4);
    margin-bottom:0.18rem;
}}
</style>

<div class="paw-field">
    <span class="paw">🐾</span><span class="paw">🐾</span><span class="paw">🐾</span>
    <span class="paw">🐾</span><span class="paw">🐾</span><span class="paw">🐾</span>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "gboy_awake"    not in st.session_state: st.session_state.gboy_awake    = False
if "gboy_messages" not in st.session_state: st.session_state.gboy_messages = []
if "gboy_waking"   not in st.session_state: st.session_state.gboy_waking   = False
if "gboy_sleeping" not in st.session_state: st.session_state.gboy_sleeping  = False

# ── Avatar section ────────────────────────────────────────────
st.markdown('<div class="gboy-center">', unsafe_allow_html=True)

if st.session_state.gboy_waking:
    st.markdown(f"""
    <div class="z-wrap">
        <img src="{img_awake}" class="gboy-waking" alt="GBoy waking"/>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.gboy_waking = False
    st.session_state.gboy_awake  = True

elif st.session_state.gboy_sleeping:
    st.markdown(f"""
    <div class="z-wrap">
        <img src="{img_sleep}" class="gboy-goingsleep" alt="GBoy going to sleep"/>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.gboy_sleeping = False

elif not st.session_state.gboy_awake:
    st.markdown(f"""
    <div class="z-wrap">
        <img src="{img_sleep}" class="gboy-sleeping" alt="GBoy sleeping"/>
        <span class="z1">Z</span>
        <span class="z2">z</span>
        <span class="z3">z</span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="avatar-ring">
        <div class="avatar-tooltip">🐾 I'm listening!</div>
        <img src="{img_awake}" class="avatar-img" alt="GBoy awake"/>
    </div>
    """, unsafe_allow_html=True)

status_color = "#66bb6a" if st.session_state.gboy_awake else "#9e9e9e"
status_text  = "ONLINE · READY TO HELP" if st.session_state.gboy_awake else "SLEEPING · CLICK TO WAKE"
st.markdown(f"""
<div class="gboy-name">🐕 GBoy</div>
<div class="gboy-tag">Labour Law Superhero · Always here to help</div>
<div class="status-badge">
    <div class="status-dot" style="background:{status_color};"></div>
    {status_text}
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Sleeping state UI ─────────────────────────────────────────
if not st.session_state.gboy_awake:
    st.markdown(f"""
    <div class="hint-box">
        😴 GBoy is fast asleep after a long day of protecting workers' rights!<br>
        <span style="font-size:0.78rem;opacity:0.7;">
            Press the button below to wake him up 🐾
        </span>
    </div>
    <div class="sleep-note">
        💤 He's dreaming about labour law... probably about gratuity calculations 😄
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🌅 Wake Up GBoy!", key="wake-gboy", use_container_width=True):
        st.session_state.gboy_waking = True
        st.rerun()

# ── Awake state UI ────────────────────────────────────────────
else:
    st.markdown(f"""
    <div class="speech-bubble">
        🐾 <b>Woof! I'm GBoy — your Labour Law Superhero!</b><br>
        Ask me anything about Indian Labour Law — your rights as an employee,
        employer duties, gratuity, PF, maternity leave, industrial disputes,
        minimum wages — I have you covered! 🏅
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.gboy_messages:
        chat_html = '<div class="chat-area">'
        for msg in st.session_state.gboy_messages:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="msg-user">
                    <div>
                        <div class="bub-label" style="text-align:right;">YOU 👤</div>
                        <div class="bub-user">{msg["content"].replace('<','&lt;').replace('>','&gt;')}</div>
                    </div>
                </div>"""
            else:
                chat_html += f"""
                <div class="msg-bot">
                    <div>
                        <div class="bub-label">🐕 GBOY</div>
                        <div class="bub-bot">{msg["content"].replace('<','&lt;').replace('>','&gt;')}</div>
                    </div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    user_input = st.chat_input("Ask GBoy anything about labour law...")
    if user_input:
        active_key = st.session_state.user_api_key or api_key
        if st.session_state.gboy_query_count >= FREE_LIMIT and not st.session_state.user_api_key:
            st.warning("⚠️ You've used your 2 free queries! Please enter your own Anthropic API key to continue.")
            user_key = st.text_input("Your Anthropic API Key:", type="password", key="gboy_key_input")
            if st.button("Submit Key"):
                st.session_state.user_api_key = user_key
                st.rerun()
            st.stop()

        st.session_state.gboy_query_count += 1
        active_key = st.session_state.user_api_key or api_key
        st.session_state.gboy_messages.append({"role":"user","content":user_input})
        with st.spinner("🐾 GBoy is thinking..."):
            try:
                client = anthropic.Anthropic(api_key=active_key)
                resp = client.messages.create(
                    model="claude-sonnet-4-6", max_tokens=1024,
                    system="""You are GBoy, a warm loyal superhero dog and expert in Indian Labour Law.
                    Speak warmly, clearly and helpfully. Always mention the relevant Act and Section.
                    Keep answers practical and easy to understand.
                    You are like a faithful companion who always has the worker's best interests at heart.""",
                    messages=[{"role":m["role"],"content":m["content"]}
                              for m in st.session_state.gboy_messages]
                )
                reply = resp.content[0].text
                st.session_state.gboy_messages.append({"role":"assistant","content":reply})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.gboy_messages = []; st.rerun()
    with c2:
        if st.button("😴 Put GBoy to Sleep", use_container_width=True):
            st.session_state.gboy_awake    = False
            st.session_state.gboy_sleeping = True
            st.session_state.gboy_messages = []
            st.rerun()

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)