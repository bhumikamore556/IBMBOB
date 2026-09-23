"""Home page — modern hero + feature cards."""
import streamlit as st


def render():
    # ── Hero ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #312e81 100%);
        border-radius: 20px;
        padding: 48px 40px;
        text-align: center;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    ">
        <div style="font-size:3.2rem; margin-bottom:12px;">📡</div>
        <h1 style="color:#f1f5f9; font-size:2.4rem; font-weight:800; margin:0 0 10px 0; letter-spacing:-0.5px;">
            AI-Powered Telecom Training Assistant
        </h1>
        <p style="color:#94a3b8; font-size:1.1rem; margin:0 auto; max-width:620px; line-height:1.7;">
            Learn telecommunications through <strong style="color:#a5b4fc;">Groq AI</strong>
            and <strong style="color:#a5b4fc;">Retrieval-Augmented Generation</strong>.
            Ask questions, explore concepts, take quizzes — all powered by your own learning materials.
        </p>
        <div style="margin-top:24px; display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
            <span style="background:rgba(99,102,241,0.2);color:#a5b4fc;padding:5px 14px;border-radius:99px;font-size:0.82rem;font-weight:600;border:1px solid rgba(99,102,241,0.3);">🤖 Groq LLM</span>
            <span style="background:rgba(16,185,129,0.15);color:#6ee7b7;padding:5px 14px;border-radius:99px;font-size:0.82rem;font-weight:600;border:1px solid rgba(16,185,129,0.25);">🔍 RAG Architecture</span>
            <span style="background:rgba(245,158,11,0.15);color:#fcd34d;padding:5px 14px;border-radius:99px;font-size:0.82rem;font-weight:600;border:1px solid rgba(245,158,11,0.25);">📊 Vector Database</span>
            <span style="background:rgba(236,72,153,0.15);color:#f9a8d4;padding:5px 14px;border-radius:99px;font-size:0.82rem;font-weight:600;border:1px solid rgba(236,72,153,0.25);">🎯 Interactive Quizzes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick-start steps ──────────────────────────────────────────────
    st.markdown("""
    <div class="fancy-divider"></div>
    <h2 style="font-weight:700; color:#1e293b; font-size:1.3rem; margin-bottom:16px;">
        🚀 Get Started in 3 Steps
    </h2>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card card-blue" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:10px;">📂</div>
            <div style="font-weight:700; font-size:1rem; color:#1e293b; margin-bottom:6px;">Step 1 — Upload</div>
            <div style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Go to <strong>Upload Materials</strong> and upload your telecom PDF documents.
                The system extracts, chunks, and embeds them automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card card-green" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:10px;">🔍</div>
            <div style="font-weight:700; font-size:1rem; color:#1e293b; margin-bottom:6px;">Step 2 — Ask</div>
            <div style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Visit <strong>Ask Assistant</strong> or the <strong>Chatbot</strong> and type
                any telecom question. Get answers grounded in your documents.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card card-pink" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:10px;">📝</div>
            <div style="font-weight:700; font-size:1rem; color:#1e293b; margin-bottom:6px;">Step 3 — Quiz</div>
            <div style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Go to <strong>Generate Quiz</strong>, pick a topic and difficulty,
                answer questions, and see your score with explanations.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Feature grid ──────────────────────────────────────────────────
    st.markdown("""
    <div class="fancy-divider"></div>
    <h2 style="font-weight:700; color:#1e293b; font-size:1.3rem; margin-bottom:16px;">
        ✨ Key Features
    </h2>
    """, unsafe_allow_html=True)

    features = [
        ("📄", "Document Upload", "Upload telecom PDFs — lecture notes, 5G specs, LTE docs. Text is automatically extracted, chunked, and indexed.", "card-blue"),
        ("🔍", "RAG Question Answering", "Questions are answered using semantically retrieved document chunks passed to Groq AI. Every answer cites its source.", "card-green"),
        ("💬", "Interactive Chatbot", "Multi-turn AI conversation that remembers context across your session. Ask follow-up questions naturally.", "card-orange"),
        ("📖", "Concept Explainer", "Get a structured breakdown of any telecom concept: definition, mechanism, real-world example, and key points.", "card-pink"),
        ("📝", "Quiz Generator", "AI generates multiple-choice quizzes on any topic at Easy, Medium, or Hard difficulty using your documents.", "card-blue"),
        ("📊", "Instant Scoring", "Submit answers and instantly see score, correct/incorrect breakdown, explanations, and study recommendations.", "card-green"),
        ("📚", "Knowledge Base", "Track all uploaded documents, chunk counts, and test retrieval directly from the browser.", "card-orange"),
        ("🔗", "Source Citations", "Every AI answer shows which document and page it came from so you can verify and study further.", "card-pink"),
    ]

    for row in range(0, len(features), 4):
        cols = st.columns(4)
        for col, (icon, title, desc, cls) in zip(cols, features[row:row+4]):
            with col:
                st.markdown(f"""
                <div class="card {cls}">
                    <div style="font-size:1.6rem; margin-bottom:8px;">{icon}</div>
                    <div style="font-weight:700; color:#1e293b; font-size:0.95rem; margin-bottom:6px;">{title}</div>
                    <div style="color:#64748b; font-size:0.85rem; line-height:1.6;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── How RAG works ──────────────────────────────────────────────────
    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

    with st.expander("🏗️  How does RAG work in this system?", expanded=False):
        st.markdown("""
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:8px;">
            <div class="card" style="flex:1; min-width:200px; text-align:center;">
                <div style="font-size:1.5rem;">📄</div>
                <div style="font-weight:700; color:#6366f1; font-size:0.9rem; margin:6px 0 4px;">1. Ingest</div>
                <div style="color:#64748b; font-size:0.82rem;">PDF → extract text → split into chunks → generate embeddings → store in ChromaDB</div>
            </div>
            <div style="display:flex; align-items:center; color:#94a3b8; font-size:1.2rem;">→</div>
            <div class="card" style="flex:1; min-width:200px; text-align:center;">
                <div style="font-size:1.5rem;">🔍</div>
                <div style="font-weight:700; color:#6366f1; font-size:0.9rem; margin:6px 0 4px;">2. Retrieve</div>
                <div style="color:#64748b; font-size:0.82rem;">Embed question → search ChromaDB → return top-K most similar document chunks</div>
            </div>
            <div style="display:flex; align-items:center; color:#94a3b8; font-size:1.2rem;">→</div>
            <div class="card" style="flex:1; min-width:200px; text-align:center;">
                <div style="font-size:1.5rem;">🤖</div>
                <div style="font-weight:700; color:#6366f1; font-size:0.9rem; margin:6px 0 4px;">3. Generate</div>
                <div style="color:#64748b; font-size:0.82rem;">Build prompt: system + context + question → Groq AI → answer + sources</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📡  Supported telecom topics"):
        topics = ["5G / NR", "4G / LTE", "OFDM", "MIMO", "Beamforming", "Modulation",
                  "Antennas & Propagation", "Base Stations", "RAN", "Core Network",
                  "Network Slicing", "Handover", "Signal Processing", "IoT Communication",
                  "Network Protocols", "Spectrum Management", "Small Cells", "mmWave",
                  "Channel Coding", "Carrier Aggregation"]
        badges = "".join(
            f'<span class="badge badge-blue" style="margin:3px;">{t}</span>' for t in topics
        )
        st.markdown(f'<div style="line-height:2.2;">{badges}</div>', unsafe_allow_html=True)
