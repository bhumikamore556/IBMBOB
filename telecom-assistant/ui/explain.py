"""Explain Concept page — modern concept card with structured output."""
import streamlit as st
from services.explanation_service import explain_concept
from models.granite_model import is_configured
from utils.helpers import TELECOM_TOPICS


def render():
    st.markdown("""
    <div class="page-title">📖 Explain Concept</div>
    <div class="page-subtitle">Get a clear, beginner-friendly explanation of any telecom concept</div>
    """, unsafe_allow_html=True)

    if not is_configured():
        st.markdown("""
        <div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:12px;
                    padding:12px 16px; margin-bottom:12px;">
            ⚠️ <strong style="color:#92400e;">Groq API key not set</strong> — add GROQ_API_KEY to your .env file to enable AI explanations.
        </div>
        """, unsafe_allow_html=True)

    # ── Topic grid (quick-pick buttons) ───────────────────────────────
    st.markdown("""
    <div style="font-weight:600; color:#1e293b; font-size:0.95rem; margin-bottom:10px;">
        ⚡ Quick-pick a common topic:
    </div>
    """, unsafe_allow_html=True)

    quick_topics = TELECOM_TOPICS[:12]
    cols = st.columns(6)
    for i, topic in enumerate(quick_topics):
        with cols[i % 6]:
            if st.button(topic, key=f"qt_{i}", use_container_width=True):
                st.session_state["explain_concept"] = topic
                st.rerun()

    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────
    prefill = st.session_state.pop("explain_concept", "5G")

    st.markdown("""
    <div style="font-weight:600; color:#1e293b; font-size:0.95rem; margin-bottom:6px;">
        ✏️ Enter any concept (or use quick-pick above):
    </div>
    """, unsafe_allow_html=True)

    concept = st.text_input(
        "concept_input",
        value=prefill,
        placeholder="e.g. OFDM, Network Slicing, Massive MIMO, mmWave…",
        label_visibility="collapsed",
    )

    if st.button("💡  Explain Simply", type="primary"):
        if not concept.strip():
            st.error("Please enter a concept.")
            return

        with st.spinner(f"Generating explanation for **{concept}**…"):
            try:
                result = explain_concept(concept)
            except Exception as exc:
                st.error(f"❌ {exc}")
                return

        # ── Result card ───────────────────────────────────────────────
        st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

        # Header
        src_badge = (
            '<span class="badge badge-green" style="margin-left:10px;">✅ From Documents</span>'
            if result["from_documents"]
            else '<span class="badge badge-blue" style="margin-left:10px;">🤖 Groq AI</span>'
        )
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:6px;">
            <span style="font-size:1.5rem;">📡</span>
            <span style="font-size:1.3rem; font-weight:800; color:#1e293b;">{concept}</span>
            {src_badge}
        </div>
        """, unsafe_allow_html=True)

        # Explanation box
        st.markdown(f"""
        <div style="background:#fafafa; border:1px solid #e2e8f0; border-radius:16px;
                    padding:28px 32px; line-height:1.85; color:#334155; font-size:0.95rem;
                    white-space:pre-wrap;">
{result["explanation"]}
        </div>
        """, unsafe_allow_html=True)

        # Sources
        if result["sources"]:
            st.markdown("<div style='margin-top:14px;'>", unsafe_allow_html=True)
            pills = "".join(
                f'<span class="source-pill">📄 {s["source"]} — p.{s["page"]}</span>'
                for s in result["sources"]
            )
            st.markdown(f'<div style="font-size:0.85rem; color:#475569; margin-bottom:4px;">📚 Sources:</div>{pills}',
                        unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
