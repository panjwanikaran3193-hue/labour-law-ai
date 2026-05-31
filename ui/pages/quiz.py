"""quiz.py — Labour Law Quiz with no-repeat questions"""
import streamlit as st, anthropic, json, os, sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, sidebar_nav, back_button
load_dotenv()

st.set_page_config(page_title="Quiz", page_icon="🎯", layout="wide")
apply_theme()
sidebar_nav("Quiz")

api_key = os.getenv("ANTHROPIC_API_KEY","")
st.markdown('<div class="page-title">🎯 Labour Law Quiz</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Test your knowledge — pick a topic and go!</div>', unsafe_allow_html=True)
back_button()

TOPICS = ["Industrial Disputes Act","Factories Act","Payment of Gratuity Act",
          "Maternity Benefit Act","Employees Provident Fund Act","Minimum Wages Act",
          "Payment of Wages Act","Contract Labour Act","Trade Unions Act","Workmen Compensation Act"]

if "quiz_questions" not in st.session_state: st.session_state.quiz_questions = []
if "quiz_topic" not in st.session_state: st.session_state.quiz_topic = ""

col1, col2, col3 = st.columns([2,1,1])
with col1: topic = st.selectbox("Choose a topic:", TOPICS)
with col2: num_q = st.slider("Questions:", 3, 10, 5)
with col3:
    st.write(""); st.write("")
    gen = st.button("🌱 Generate Quiz", use_container_width=True)

if gen and api_key:
    with st.spinner("🌿 Generating unique questions..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=2500,
                system="""Generate MCQ questions about Indian Labour Law. 
                IMPORTANT: Make every question UNIQUE — do not repeat similar questions.
                Return ONLY a valid JSON array, no other text, no markdown.
                Format: [{"question":"...","options":["A)...","B)...","C)...","D)..."],"answer":"A","explanation":"..."}]""",
                messages=[{"role":"user","content":
                    f"Generate exactly {num_q} UNIQUE, NON-REPEATING MCQ questions about {topic} under Indian Labour Law. "
                    f"Cover different sections, provisions and aspects. Return only valid JSON array."}]
            )
            raw = resp.content[0].text.strip()
            for fence in ["```json","```"]: raw = raw.replace(fence,"")
            st.session_state.quiz_questions = json.loads(raw.strip())
            st.session_state.quiz_topic = topic
            st.rerun()
        except Exception as e:
            st.error(f"Error generating quiz: {e}")

if st.session_state.quiz_questions:
    st.markdown(f"""
    <div class="field-card">
        <b style="color:#1b5e20;font-family:'Playfair Display',serif;font-size:1.1rem;">
        📋 {st.session_state.quiz_topic} — {len(st.session_state.quiz_questions)} Questions
        </b>
    </div>
    """, unsafe_allow_html=True)

    score = 0
    for i, q in enumerate(st.session_state.quiz_questions):
        with st.expander(f"Q{i+1}. {q['question']}", expanded=True):
            choice = st.radio("", q["options"], key=f"q_{i}", index=None)
            if choice:
                if choice[0] == q["answer"]: st.success("✅ Correct!"); score += 1
                else: st.error(f"❌ Wrong. Correct: {q['answer']}")
                st.info(f"💡 {q['explanation']}")
    st.divider()
    total = len(st.session_state.quiz_questions)
    pct = int(score/total*100) if total else 0
    c1, c2 = st.columns(2)
    with c1: st.metric("🏆 Score", f"{score} / {total}", f"{pct}%")
    with c2:
        if pct >= 70: st.success("🌟 Excellent!")
        elif pct >= 50: st.warning("🌱 Good effort!")
        else: st.error("📖 Keep studying!")
    if st.button("🔄 New Quiz"): st.session_state.quiz_questions = []; st.rerun()

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)
