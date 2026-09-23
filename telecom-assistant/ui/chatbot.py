"""Chatbot page — modern chat bubbles with source pills."""
import streamlit as st
from services.qa_service import answer_with_chat_history
from models.granite_model import is_configured


def render():
    st.markdown("""
    <div class="page-title">💬 Telecom AI Chatbot</div>
    <div class="page-subtitle">Have a multi-turn conversation about any telecom topic</div>
    """, unsafe_allow_html=True)

    if not is_configured():
        st.markdown("""
        <div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:12px;
                    padding:12px 16px; margin-bottom:12px;">
            ⚠️ <strong style="color:#92400e;">Groq API key not configured</strong> —
            add GROQ_API_KEY to your .env file, then restart.
        </div>
        """, unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Sidebar controls ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="font-weight:700; color:#e2e8f0; font-size:0.9rem; margin-bottom:10px;">
            💬 Chat Controls
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️  Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        st.markdown("""
        <div style="height:1px; background:#334155; margin:12px 0;"></div>
        <div style="font-size:0.78rem; color:#94a3b8; font-weight:600; margin-bottom:6px;">
            EXAMPLE QUESTIONS
        </div>
        """, unsafe_allow_html=True)
        examples = [
            "What is 5G?", "Explain MIMO.", "Difference between LTE and 5G?",
            "How does handover work?", "What is beamforming?",
            "Explain OFDM with an example.", "What is the core network?",
        ]
        for ex in examples:
            st.caption(f"• {ex}")

    # ── Tip bar (shown when no history) ───────────────────────────────
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e293b,#312e81); border-radius:14px;
                    padding:20px 24px; margin-bottom:20px; color:#e2e8f0; text-align:center;">
            <div style="font-size:2rem; margin-bottom:8px;">💬</div>
            <div style="font-weight:700; font-size:1rem; margin-bottom:6px;">Start a conversation</div>
            <div style="font-size:0.87rem; color:#94a3b8; max-width:500px; margin:0 auto;">
                Ask anything about telecom — 5G, LTE, OFDM, MIMO, antennas, protocols, and more.
                Your uploaded documents will be used to ground the answers.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────
    for turn in st.session_state.chat_history:
        if turn["role"] == "user":
            with st.chat_message("user"):
                st.markdown(turn["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(turn["content"])
                if turn.get("sources"):
                    pills = "".join(
                        f'<span class="source-pill">📄 {s["source"]} p.{s["page"]}</span>'
                        for s in turn["sources"]
                    )
                    st.markdown(
                        f'<div style="margin-top:8px; font-size:0.82rem; color:#64748b;">📚 Sources: {pills}</div>',
                        unsafe_allow_html=True,
                    )
                elif turn.get("general"):
                    st.caption("ℹ️ General knowledge — upload documents for grounded answers.")

    # ── Input ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a telecom question…")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    result = answer_with_chat_history(
                        question=user_input,
                        chat_history=st.session_state.chat_history[:-1],
                    )
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    from_docs = result.get("from_documents", False)

                    st.markdown(answer)

                    if from_docs and sources:
                        pills = "".join(
                            f'<span class="source-pill">📄 {s["source"]} p.{s["page"]}</span>'
                            for s in sources
                        )
                        st.markdown(
                            f'<div style="margin-top:8px; font-size:0.82rem; color:#64748b;">📚 Sources: {pills}</div>',
                            unsafe_allow_html=True,
                        )
                    elif not from_docs:
                        st.caption("ℹ️ General knowledge — upload documents for grounded answers.")

                except Exception as exc:
                    answer = f"⚠️ Error: {exc}"
                    sources = []
                    from_docs = False
                    st.error(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "general": not from_docs,
        })
