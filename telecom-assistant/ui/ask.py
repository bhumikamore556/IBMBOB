"""Ask Telecom Assistant page — modern answer cards with source badges."""
import streamlit as st
from services.qa_service import answer_question
from models.granite_model import is_configured
from rag.vector_store import get_knowledge_base_info


_EXAMPLES = [
    "What is the difference between 4G and 5G?",
    "Explain OFDM in simple words.",
    "How does MIMO improve data rates?",
    "What is network slicing in 5G?",
    "Explain the 5G core network architecture.",
    "What is beamforming and why is it used?",
    "What is the role of the RAN?",
    "How does handover work in LTE?",
]


def render():
    st.markdown("""
    <div class="page-title">🔍 Ask Telecom Assistant</div>
    <div class="page-subtitle">Ask any telecom question — answers are grounded in your uploaded documents</div>
    """, unsafe_allow_html=True)

    # ── Status banners ────────────────────────────────────────────────
    if not is_configured():
        st.markdown("""
        <div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:12px;
                    padding:12px 16px; margin-bottom:12px; display:flex; gap:10px; align-items:center;">
            <span style="font-size:1.3rem;">⚠️</span>
            <div>
                <strong style="color:#92400e;">Groq API key not configured</strong><br>
                <span style="color:#78350f; font-size:0.87rem;">Add GROQ_API_KEY to your .env file, then restart.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    try:
        kb_info = get_knowledge_base_info()
        has_docs = kb_info["total_chunks"] > 0
    except Exception:
        has_docs = False

    if not has_docs:
        st.markdown("""
        <div style="background:#ede9fe; border:1px solid #c4b5fd; border-radius:12px;
                    padding:12px 16px; margin-bottom:12px; display:flex; gap:10px; align-items:center;">
            <span style="font-size:1.3rem;">📂</span>
            <div>
                <strong style="color:#4338ca;">No documents uploaded yet</strong><br>
                <span style="color:#4c1d95; font-size:0.87rem;">
                    Go to <strong>Upload Materials</strong> to add telecom PDFs for document-grounded answers.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Example questions ─────────────────────────────────────────────
    with st.expander("💡  Example questions — click to use"):
        cols = st.columns(2)
        for i, q in enumerate(_EXAMPLES):
            with cols[i % 2]:
                if st.button(q, key=f"eq_{i}"):
                    st.session_state["prefill_q"] = q
                    st.rerun()

    # ── Question input ────────────────────────────────────────────────
    prefill = st.session_state.pop("prefill_q", "")

    st.markdown("""
    <div style="font-weight:600; color:#1e293b; font-size:0.95rem; margin:16px 0 6px 0;">
        ✏️ Your Question
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area(
        "question_input",
        value=prefill,
        placeholder="e.g. What is the difference between 4G and 5G?",
        height=100,
        label_visibility="collapsed",
    )

    col_a, col_b = st.columns([3, 1])
    with col_b:
        top_k = st.selectbox("Chunks to retrieve", [2, 3, 4, 6, 8], index=2,
                              help="More chunks = broader context")
    with col_a:
        ask_btn = st.button("🚀  Get Answer", type="primary", use_container_width=True)

    if ask_btn:
        if not question.strip():
            st.error("Please enter a question.")
            return

        with st.spinner("Searching knowledge base and generating answer…"):
            try:
                result = answer_question(question=question, top_k=top_k)
            except Exception as exc:
                st.error(f"❌ {exc}")
                return

        # ── Answer card ───────────────────────────────────────────────
        st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

        if result["from_documents"]:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                <span class="badge badge-green">✅ From Documents</span>
                <span style="color:#64748b; font-size:0.85rem;">{result['chunks_used']} chunks retrieved</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                <span class="badge badge-orange">⚠️ General Knowledge</span>
                <span style="color:#64748b; font-size:0.85rem;">Upload documents for grounded answers</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#fafafa; border:1px solid #e2e8f0; border-radius:16px;
                    padding:24px 28px; margin-bottom:16px; line-height:1.8;">
            <div style="font-weight:700; color:#1e293b; margin-bottom:12px; font-size:1rem;">
                📋 Answer
            </div>
            <div style="color:#334155; font-size:0.95rem; white-space:pre-wrap;">{result["answer"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Sources ───────────────────────────────────────────────────
        if result["sources"]:
            st.markdown("""
            <div style="font-weight:600; color:#475569; font-size:0.88rem; margin-bottom:8px;">
                📚 Sources used to generate this answer:
            </div>
            """, unsafe_allow_html=True)
            pills = "".join(
                f'<span class="source-pill">📄 {s["source"]} — p.{s["page"]}</span>'
                for s in result["sources"]
            )
            st.markdown(f'<div style="margin-bottom:4px;">{pills}</div>', unsafe_allow_html=True)
