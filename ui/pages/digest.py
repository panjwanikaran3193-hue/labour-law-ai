"""digest.py — Knowledge Digest — Essentials / Expert — file list after question box"""
import streamlit as st, anthropic, os, sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, sidebar_nav, back_button
load_dotenv()

st.set_page_config(page_title="Knowledge Digest", page_icon="📚", layout="wide")
apply_theme()
sidebar_nav("Knowledge Digest")

api_key = os.getenv("ANTHROPIC_API_KEY","")
ROOT = Path(__file__).resolve().parents[2]
FOLDERS = {
    "⚖️ Acts": ROOT/"acts", "📋 Rules": ROOT/"rules",
    "🏛️ Judgments": ROOT/"judgments", "📢 Circulars": ROOT/"circulars",
    "📝 Forms": ROOT/"forms", "❓ FAQs": ROOT/"faq",
}

st.markdown('<div class="page-title">📚 Knowledge Digest</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Understand Indian Labour Law — at your own level</div>', unsafe_allow_html=True)
back_button()

# ── Level selector ──────────────────────────────────────────
st.markdown("""
<style>
.level-row { display:flex; gap:1rem; margin-bottom:1rem; }
.lv {
    flex:1; border-radius:18px; padding:1rem 1.2rem; cursor:pointer;
    text-align:center; border:3px solid transparent; transition:all 0.2s;
}
.lv-e { background:linear-gradient(145deg,#fff8e1,#fff3cd); border-color:#ffb300;
         box-shadow:0 5px 0 #f59e0b,0 7px 15px rgba(245,158,11,0.2); }
.lv-x { background:linear-gradient(145deg,#e8eaf6,#c5cae9); border-color:#5c6bc0;
         box-shadow:0 5px 0 #3949ab,0 7px 15px rgba(57,73,171,0.2); }
.lv-title { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:900; }
.lv-desc  { font-size:0.78rem; margin-top:0.3rem; }
</style>
<div class="level-row">
  <div class="lv lv-e">
    <div class="lv-title" style="color:#92400e;">🌱 Essentials</div>
    <div class="lv-desc" style="color:#78350f;">Plain English · Perfect for employees, HR & beginners</div>
  </div>
  <div class="lv lv-x">
    <div class="lv-title" style="color:#1a237e;">🎓 Expert</div>
    <div class="lv-desc" style="color:#283593;">Deep legal analysis · Sections & case law · For lawyers & senior HR</div>
  </div>
</div>
""", unsafe_allow_html=True)

level = st.radio("Your level:", ["🌱 Essentials — plain English for everyone",
                                  "🎓 Expert — detailed legal analysis"],
                 label_visibility="collapsed")
is_expert = "Expert" in level
st.divider()

# ── ASK QUESTION FIRST ──────────────────────────────────────
if is_expert:
    st.markdown("### 🎓 Expert Legal Analysis")
    placeholder = "e.g. Section 25F Industrial Disputes Act, retrenchment compensation proviso"
    system_prompt = """You are a senior Indian Labour Law advocate. Give detailed legal analysis 
    with specific section numbers, sub-sections, relevant case law citations, exceptions, 
    judicial interpretations, and practical implications. Use proper legal terminology."""
    model = "claude-opus-4-6"
else:
    st.markdown("### 🌱 Essentials — Simple Explanation")
    placeholder = "e.g. What is Gratuity? How many leaves do I get? What is minimum wage?"
    system_prompt = """You are a friendly Indian Labour Law guide. Explain in very simple plain English. 
    No heavy legal jargon. Short sentences, bullet points, real-world examples. 
    Imagine explaining to someone with zero legal background."""
    model = "claude-sonnet-4-6"

topic = st.text_input("Enter a topic:", placeholder=placeholder)

if st.button("📖 Explain This Topic") and topic:
    if not api_key or "your-key" in api_key:
        st.error("⚠️ Add your ANTHROPIC_API_KEY to .env first.")
    else:
        with st.spinner("Fetching explanation..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                resp = client.messages.create(
                    model=model, max_tokens=1500,
                    system=system_prompt,
                    messages=[{"role":"user","content":f"Explain: {topic} under Indian Labour Law"}]
                )
                st.markdown(f"""
                <div class="field-card">
                    <b style="color:#1b5e20; font-family:'Playfair Display',serif;">
                    {'🎓 Expert Analysis' if is_expert else '🌱 Simple Explanation'}
                    </b><br><br>
                    {resp.content[0].text.replace(chr(10),'<br>')}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()

# ── DOCUMENT LIBRARY BELOW ──────────────────────────────────
st.markdown("### 📂 Your Document Library")
selected = st.selectbox("Browse category:", list(FOLDERS.keys()))
folder = FOLDERS[selected]
folder.mkdir(exist_ok=True)
files = list(folder.glob("*.*"))

if not files:
    st.markdown(f"""
    <div class="field-card" style="text-align:center; opacity:0.7;">
        <div style="font-size:2rem;">📭</div>
        <b>No files in {selected} yet</b><br>
        <span style="font-size:0.82rem; color:#558b2f;">Add PDFs to: <code>{folder}</code></span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"📂 {len(files)} document(s) found")
    # Show as compact illustrative tags, not full path list
    tags_html = ""
    for f in files:
        clean_name = f.stem.replace("_"," ").replace("-"," ").title()
        tags_html += f'<span style="display:inline-block; background:rgba(255,255,255,0.7); border:1.5px solid rgba(255,255,255,0.5); border-radius:20px; padding:0.25rem 0.7rem; margin:0.2rem; font-size:0.8rem; color:#1b5e20; font-weight:600; backdrop-filter:blur(4px);">📄 {clean_name}</span>'
    st.markdown(f'<div style="margin:0.5rem 0;">{tags_html}</div>', unsafe_allow_html=True)

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)
