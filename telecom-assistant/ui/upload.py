"""Upload Materials page — modern card design."""
import os
import streamlit as st
from config.settings import settings
from rag.document_loader import load_pdf_from_bytes
from rag.text_splitter import split_documents
from rag.vector_store import add_documents, get_knowledge_base_info, delete_collection
from utils.helpers import format_file_size, ensure_dir


def render():
    st.markdown("""
    <div class="page-title">📂 Upload Learning Materials</div>
    <div class="page-subtitle">Add telecom PDF documents to build the AI knowledge base</div>
    """, unsafe_allow_html=True)

    # ── Upload zone ───────────────────────────────────────────────────
    st.markdown("""
    <div class="card card-blue">
        <div style="font-weight:700; color:#1e293b; font-size:1rem; margin-bottom:4px;">📄 Select PDF Files</div>
        <div style="color:#64748b; font-size:0.87rem;">Supported: telecom textbooks, 5G/4G/LTE specs, lecture notes, protocol documents</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # ── Chunk settings ────────────────────────────────────────────────
    with st.expander("⚙️  Advanced chunking settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.slider("Chunk size (characters)", 200, 2000,
                                   settings.CHUNK_SIZE, 100,
                                   help="Larger = more context per chunk")
        with col2:
            chunk_overlap = st.slider("Chunk overlap", 0, 500,
                                      settings.CHUNK_OVERLAP, 50,
                                      help="Overlap preserves sentence continuity")

    if not uploaded_files:
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP

    # ── File list preview ─────────────────────────────────────────────
    if uploaded_files:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin:12px 0;">
            <div style="font-weight:600; color:#475569; font-size:0.88rem; margin-bottom:10px;">
                {len(uploaded_files)} file(s) ready to process
            </div>
        """, unsafe_allow_html=True)
        for f in uploaded_files:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid #f1f5f9;">
                <span style="font-size:1.2rem;">📄</span>
                <span style="font-weight:500; color:#1e293b; font-size:0.9rem; flex:1;">{f.name}</span>
                <span class="badge badge-blue">{format_file_size(f.size)}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("⚙️  Process & Add to Knowledge Base", type="primary"):
            _process_files(uploaded_files, chunk_size, chunk_overlap)

    # ── KB summary ────────────────────────────────────────────────────
    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <h3 style="font-weight:700; color:#1e293b; font-size:1.1rem; margin-bottom:12px;">
        📚 Current Knowledge Base
    </h3>
    """, unsafe_allow_html=True)
    _show_kb_summary()

    # ── Reset ─────────────────────────────────────────────────────────
    with st.expander("⚠️  Danger zone — clear knowledge base"):
        st.warning("Clearing removes **all** processed documents and embeddings. This cannot be undone.")
        if st.button("🗑️  Clear Knowledge Base", type="secondary"):
            try:
                delete_collection()
                st.success("Knowledge base cleared.")
                st.rerun()
            except Exception as exc:
                st.error(f"Failed: {exc}")


def _process_files(uploaded_files, chunk_size, chunk_overlap):
    total_chunks = 0
    errors = []
    bar = st.progress(0)
    status = st.empty()

    for i, f in enumerate(uploaded_files):
        bar.progress(i / len(uploaded_files))
        try:
            status.markdown(f"""
            <div style="background:#ede9fe; border-radius:10px; padding:10px 16px; font-size:0.9rem; color:#4338ca;">
                ⏳ Processing <strong>{f.name}</strong>…
            </div>""", unsafe_allow_html=True)

            file_bytes = f.read()
            if not file_bytes:
                errors.append(f"{f.name}: File is empty.")
                continue

            docs = load_pdf_from_bytes(file_bytes, f.name)
            chunks = split_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            if not chunks:
                errors.append(f"{f.name}: No text chunks produced.")
                continue

            ensure_dir(settings.DOCUMENTS_PATH)
            with open(os.path.join(settings.DOCUMENTS_PATH, f.name), "wb") as fh:
                fh.write(file_bytes)

            added = add_documents(chunks)
            total_chunks += added

        except Exception as exc:
            errors.append(f"{f.name}: {exc}")

    bar.progress(1.0)
    status.empty()

    if total_chunks > 0:
        st.markdown(f"""
        <div style="background:#d1fae5; border:1px solid #6ee7b7; border-radius:12px; padding:16px 20px; margin:8px 0;">
            <span style="font-size:1.2rem;">✅</span>
            <strong style="color:#065f46;"> {total_chunks} chunks</strong>
            <span style="color:#047857;"> added to the knowledge base. Ready for questions!</span>
        </div>
        """, unsafe_allow_html=True)

    for err in errors:
        st.error(f"❌ {err}")


def _show_kb_summary():
    try:
        info = get_knowledge_base_info()
    except Exception as exc:
        st.error(f"Could not read knowledge base: {exc}")
        return

    c1, c2, c3 = st.columns(3)
    _metric_card(c1, str(info["num_documents"]), "Documents")
    _metric_card(c2, str(info["total_chunks"]), "Chunks Indexed")
    _metric_card(c3, "✅ Ready" if info["total_chunks"] > 0 else "⚠️ Empty", "Status",
                 green=info["total_chunks"] > 0)

    if info["documents"]:
        st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
        for doc in info["documents"]:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; padding:8px 12px;
                        background:#f8fafc; border-radius:8px; margin-bottom:6px;
                        border:1px solid #e2e8f0;">
                <span>📄</span>
                <span style="font-weight:500; color:#1e293b; font-size:0.9rem;">{doc}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No documents yet. Upload a PDF above to get started.")


def _metric_card(col, value, label, green=None):
    if green is None:
        bg = "linear-gradient(135deg,#6366f1,#8b5cf6)"
    elif green:
        bg = "linear-gradient(135deg,#10b981,#059669)"
    else:
        bg = "linear-gradient(135deg,#f59e0b,#d97706)"
    with col:
        st.markdown(f"""
        <div style="background:{bg}; color:#fff; border-radius:14px; padding:20px;
                    text-align:center; margin-bottom:12px;">
            <div style="font-size:1.8rem; font-weight:800;">{value}</div>
            <div style="font-size:0.82rem; opacity:0.85; margin-top:4px;">{label}</div>
        </div>
        """, unsafe_allow_html=True)
