"""Knowledge Base page — modern stats cards with document list."""
import os
import streamlit as st
from rag.vector_store import get_knowledge_base_info
from config.settings import settings


def render():
    st.markdown("""
    <div class="page-title">📚 Knowledge Base</div>
    <div class="page-subtitle">View all uploaded documents, chunk statistics, and test retrieval</div>
    """, unsafe_allow_html=True)

    try:
        info = get_knowledge_base_info()
    except Exception as exc:
        st.error(f"Could not read knowledge base: {exc}")
        return

    # ── Metric cards ──────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    _mcard(c1, str(info["num_documents"]), "Documents", "#6366f1", "#8b5cf6")
    _mcard(c2, str(info["total_chunks"]), "Chunks Indexed", "#0ea5e9", "#0284c7")
    _mcard(c3,
           "✅ Ready" if info["total_chunks"] > 0 else "⚠️ Empty",
           "Status",
           "#10b981" if info["total_chunks"] > 0 else "#f59e0b",
           "#059669" if info["total_chunks"] > 0 else "#d97706")

    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

    # ── Document list ─────────────────────────────────────────────────
    if info["documents"]:
        st.markdown("""
        <h3 style="font-weight:700; color:#1e293b; font-size:1.05rem; margin-bottom:12px;">
            📄 Uploaded Learning Materials
        </h3>
        """, unsafe_allow_html=True)

        for doc in info["documents"]:
            fp = os.path.join(settings.DOCUMENTS_PATH, doc)
            size_str = ""
            if os.path.exists(fp):
                b = os.path.getsize(fp)
                size_str = f"{b/1024:.1f} KB" if b < 1024**2 else f"{b/1024**2:.1f} MB"

            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between;
                        padding:12px 16px; background:#fafafa; border:1px solid #e2e8f0;
                        border-radius:12px; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.3rem;">📄</span>
                    <span style="font-weight:600; color:#1e293b; font-size:0.92rem;">{doc}</span>
                </div>
                <span class="badge badge-blue">{size_str or "on disk"}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#f8fafc; border:2px dashed #cbd5e1; border-radius:16px;
                    padding:40px; text-align:center; color:#94a3b8; margin:16px 0;">
            <div style="font-size:2.5rem; margin-bottom:10px;">📂</div>
            <div style="font-weight:600; font-size:1rem; color:#64748b;">No documents yet</div>
            <div style="font-size:0.87rem; margin-top:4px;">
                Upload telecom PDFs on the <strong>Upload Materials</strong> page to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

    # ── Config table ──────────────────────────────────────────────────
    with st.expander("⚙️  System configuration"):
        st.markdown(f"""
        <div style="background:#f8fafc; border-radius:12px; padding:16px 20px; font-size:0.88rem;">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                <div><strong>Chunk size:</strong> {settings.CHUNK_SIZE} chars</div>
                <div><strong>Chunk overlap:</strong> {settings.CHUNK_OVERLAP} chars</div>
                <div><strong>Embedding model:</strong> {settings.EMBEDDING_MODEL}</div>
                <div><strong>Top-K retrieval:</strong> {settings.RETRIEVAL_TOP_K} chunks</div>
                <div><strong>Groq Model:</strong> {settings.GROQ_MODEL}</div>
                <div><strong>Vector store:</strong> {settings.VECTOR_STORE_PATH}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Retrieval test ────────────────────────────────────────────────
    st.markdown("""
    <h3 style="font-weight:700; color:#1e293b; font-size:1.05rem; margin-bottom:10px;">
        🔍 Test Retrieval
    </h3>
    <p style="color:#64748b; font-size:0.88rem; margin-bottom:12px;">
        Enter any query to see what the retriever finds in your knowledge base.
    </p>
    """, unsafe_allow_html=True)

    test_q = st.text_input("Test query", placeholder="e.g. What is OFDM?",
                            label_visibility="visible")
    if st.button("🔎  Search", type="primary") and test_q:
        try:
            from rag.retriever import retrieve
            chunks = retrieve(test_q, top_k=3)
            if chunks:
                st.markdown(f"""
                <div class="badge badge-green" style="margin-bottom:10px;">
                    ✅ Found {len(chunks)} chunk(s)
                </div>
                """, unsafe_allow_html=True)
                for i, c in enumerate(chunks, 1):
                    src = c["metadata"].get("source", "Unknown")
                    page = c["metadata"].get("page", "?")
                    dist = round(c.get("distance", 0), 4)
                    with st.expander(f"Chunk {i} — {src}  (p.{page})  distance: {dist}"):
                        st.markdown(f"""
                        <div style="background:#f8fafc; border-radius:10px; padding:14px;
                                    font-size:0.88rem; color:#334155; line-height:1.7;">
                            {c["page_content"][:600]}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No relevant chunks found. Try a different query.")
        except Exception as exc:
            st.error(f"Retrieval error: {exc}")


def _mcard(col, value, label, c1, c2):
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{c1},{c2}); color:#fff;
                    border-radius:14px; padding:20px; text-align:center; margin-bottom:12px;">
            <div style="font-size:1.8rem; font-weight:800;">{value}</div>
            <div style="font-size:0.82rem; opacity:0.85; margin-top:4px;">{label}</div>
        </div>
        """, unsafe_allow_html=True)
