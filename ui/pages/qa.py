"""qa.py — Legal Q&A"""
import streamlit as st, anthropic, os, sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parents[1]))
from theme import apply_theme, sidebar_nav, back_button
load_dotenv()

st.set_page_config(page_title="Legal Q&A", page_icon="💬", layout="wide")
apply_theme()
sidebar_nav("Legal Q&A")

api_key = os.getenv("ANTHROPIC_API_KEY","")
FREE_LIMIT = int(os.getenv("FREE_QUERY_LIMIT", "2"))
if "qa_query_count" not in st.session_state:
    st.session_state.qa_query_count = 0
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
st.markdown('<div class="page-title">💬 Legal Q&A</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Ask any question about Indian Labour Law</div>', unsafe_allow_html=True)
back_button()

if not api_key or "your-key" in api_key:
    st.error("⚠️ Please add your ANTHROPIC_API_KEY to the .env file first.")
    st.stop()

if "qa_messages" not in st.session_state:
    st.session_state.qa_messages = []

for msg in st.session_state.qa_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Type your labour law question here...")
if question:
    active_key = st.session_state.user_api_key or api_key
    if st.session_state.qa_query_count >= FREE_LIMIT and not st.session_state.user_api_key:
        st.warning("⚠️ You've used your 2 free queries! Please enter your own Anthropic API key to continue.")
        user_key = st.text_input("Your Anthropic API Key:", type="password", key="qa_key_input")
        if st.button("Submit Key"):
            st.session_state.user_api_key = user_key
            st.rerun()
        st.stop()

    st.session_state.qa_query_count += 1
    active_key = st.session_state.user_api_key or api_key
    st.session_state.qa_messages.append({"role":"user","content":question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("🌿 Finding your answer..."):
            try:
                client = anthropic.Anthropic(api_key=active_key)
                resp = client.messages.create(
                    model="claude-sonnet-4-6", max_tokens=1024,
                    system="""You are an expert Indian Labour Law assistant. Answer clearly 
                    and accurately. Always mention the relevant Act and Section number. 
                    Keep answers practical and easy to understand.""",
                    messages=[{"role":m["role"],"content":m["content"]}
                              for m in st.session_state.qa_messages]
                )
                answer = resp.content[0].text
                st.write(answer)
                st.session_state.qa_messages.append({"role":"assistant","content":answer})
            except Exception as e:
                st.error(f"Error: {e}")
if st.session_state.qa_messages:
    if st.button("🗑️ Clear Chat"): st.session_state.qa_messages = []; st.rerun()

st.markdown('<div class="grass-strip">🌱🌿🍃🌾🌿🌱🌾🍃🌿🌱</div>', unsafe_allow_html=True)
