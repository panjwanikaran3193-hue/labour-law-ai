"""gaps.py — Admin Gap Detector — password protected"""
import streamlit as st, anthropic, os, sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, back_button
load_dotenv()

st.set_page_config(page_title="Admin", page_icon="🔒", layout="wide")
apply_theme()

ADMIN_PASSWORD = "Agra@130793"
api_key = os.getenv("ANTHROPIC_API_KEY","")
ROOT = Path(__file__).resolve().parents[2]

if "gap_auth" not in st.session_state: st.session_state.gap_auth = False

if not st.session_state.gap_auth:
    st.markdown("""
    <div style="max-width:380px; margin:5rem auto; text-align:center;">
        <div style="font-size:4rem; margin-bottom:0.5rem;">🔒</div>
        <div style="font-family:'Playfair Display',serif; font-size:2rem;
                    font-weight:900; color:#1b5e20; margin-bottom:0.3rem;">Admin Access</div>
        <div style="color:#558b2f; font-size:0.88rem; margin-bottom:1.5rem;">
            This area is restricted to administrators only.
        </div>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        pwd = st.text_input("Password:", type="password", placeholder="Enter admin password")
        if st.button("🔓 Unlock", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.gap_auth = True; st.rerun()
            else:
                st.error("❌ Incorrect password.")
    st.stop()

# ── Authenticated ───────────────────────────────────────────
st.markdown('<div class="page-title">🔍 Knowledge Gap Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Admin view — analyse your knowledge base</div>', unsafe_allow_html=True)
back_button()

c_lock, _ = st.columns([1,4])
with c_lock:
    if st.button("🔒 Lock & Exit"): st.session_state.gap_auth = False; st.rerun()

st.divider()
FOLDERS = {
    "Acts": ROOT/"acts","Rules": ROOT/"rules","Judgments": ROOT/"judgments",
    "Circulars": ROOT/"circulars","Forms": ROOT/"forms","FAQs": ROOT/"faq","Summaries": ROOT/"summaries",
}
counts = {}
cols = st.columns(len(FOLDERS))
for i,(name,folder) in enumerate(FOLDERS.items()):
    folder.mkdir(exist_ok=True)
    count = len(list(folder.glob("*.*"))); counts[name]=count
    with cols[i]:
        color = "#ffcdd2" if count==0 else "#c8e6c9" if count>=5 else "#fff9c4"
        st.markdown(f"""<div style="background:{color};border:2px solid rgba(255,255,255,0.5);
            border-radius:14px;padding:0.8rem;text-align:center;backdrop-filter:blur(4px);">
            <div style="font-size:1.5rem;font-weight:900;color:#1b5e20;">{count}</div>
            <div style="font-size:0.72rem;color:#558b2f;font-weight:700;">{name}</div>
        </div>""", unsafe_allow_html=True)

st.markdown(f"<br><b>Total: {sum(counts.values())} documents</b>", unsafe_allow_html=True)
st.divider()

if st.button("🤖 Analyse Gaps with Claude", use_container_width=True):
    with st.spinner("Analysing..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-6", max_tokens=1500,
                system="You are an Indian Labour Law expert helping build a comprehensive knowledge base.",
                messages=[{"role":"user","content":f"""
                My knowledge base has: {counts}. Total: {sum(counts.values())} docs.
                Tell me: 1) Critical missing Acts, 2) Missing Rules/Notifications, 
                3) Valuable Judgment types, 4) Priority order to add next, 5) Completeness score /10.
                """}]
            )
            st.markdown(f'<div class="field-card">{resp.content[0].text.replace(chr(10),"<br>")}</div>',
                       unsafe_allow_html=True)
        except Exception as e: st.error(f"Error: {e}")

st.divider()
st.subheader("📁 File Details")
for name,folder in FOLDERS.items():
    files = list(folder.glob("*.*"))
    if files:
        with st.expander(f"{name} — {len(files)} files"):
            for f in files:
                st.write(f"📄 {f.name} ({f.stat().st_size:,} bytes)")

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)
