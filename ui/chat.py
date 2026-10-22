"""Module 9: Streamlit demo UI."""
import requests
import streamlit as st

API = "http://localhost:8000"
st.set_page_config(page_title="EdTech Support Assistant", page_icon="🎓")
st.title("🎓 Student Support Assistant")
st.caption("Ask in English, தமிழ், or Tanglish. Answers come only from approved help articles.")

student = st.sidebar.selectbox("Log in as student", [1, 2, 3])
st.sidebar.info("Switch students to see that each one only sees their own data.")
if st.session_state.get("student") != student:        # new login -> new token, new chat
    r = requests.post(f"{API}/dev/token/{student}", timeout=10)
    st.session_state.update(student=student, token=r.json()["token"], history=[])

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["text"])
        if m.get("meta"):
            st.caption(m["meta"])

if q := st.chat_input("Ask a question / கேள்வி கேளுங்கள்"):
    st.session_state.history.append({"role": "user", "text": q})
    with st.chat_message("user"):
        st.markdown(q)
    resp = requests.post(f"{API}/chat", json={"message": q}, timeout=30,
        headers={"Authorization": f"Bearer {st.session_state.token}"})
    if resp.status_code != 200:
        text, meta = f"⚠️ {resp.json().get('detail', 'Error')}", ""
    else:
        r = resp.json()
        text = r["reply"]
        parts = [f"⏱ {r['latency_ms']} ms", f"lang: {r['lang']}", f"action: {r['action']}"]
        if r.get("source"):
            parts.append(f"source: {r['source']}")
        if r.get("score"):
            parts.append(f"score: {r['score']}")
        if r.get("cached"):
            parts.append("⚡ cached")
        if r.get("escalated"):
            parts.append(f"🎫 ticket {r.get('ticket_id')} ({r.get('category')})")
        meta = " · ".join(parts)
    with st.chat_message("assistant"):
        st.markdown(text)
        st.caption(meta)
    st.session_state.history.append({"role": "assistant", "text": text, "meta": meta})
