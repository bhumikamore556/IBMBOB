"""
app.py — Main entry point for the AI-Powered Telecom Training Assistant.

Run with:
    streamlit run app.py
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="Telecom Training Assistant",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 4px;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    display: flex !important;
    align-items: center;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.92rem;
    font-weight: 500;
    transition: background 0.2s, color 0.2s;
    border: 1px solid transparent;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.3);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: rgba(99,102,241,0.25) !important;
    border-color: #6366f1 !important;
    color: #a5b4fc !important;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
.card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.10); transform: translateY(-2px); }

.card-blue  { border-left: 4px solid #6366f1; }
.card-green { border-left: 4px solid #10b981; }
.card-orange{ border-left: 4px solid #f59e0b; }
.card-pink  { border-left: 4px solid #ec4899; }

/* ── Metric badges ── */
.metric-card {
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: #fff !important;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.metric-card .num { font-size: 2rem; font-weight: 800; }
.metric-card .lbl { font-size: 0.82rem; opacity: 0.85; margin-top: 2px; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.94rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
}

/* ── Alerts ── */
.stSuccess { border-radius: 10px !important; }
.stWarning { border-radius: 10px !important; }
.stError   { border-radius: 10px !important; }
.stInfo    { border-radius: 10px !important; }

/* ── Expander ── */
.stExpander { border-radius: 12px !important; border: 1px solid #e2e8f0 !important; }

/* ── Progress bar ── */
.stProgress > div > div { background: linear-gradient(90deg,#6366f1,#8b5cf6) !important; border-radius: 99px !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] { border-radius: 14px !important; margin-bottom: 8px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { color: #6366f1 !important; border-bottom-color: #6366f1 !important; }

/* ── Page title ── */
.page-title {
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.page-subtitle {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

/* ── Tag / badge ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-blue   { background:#ede9fe; color:#6366f1; }
.badge-green  { background:#d1fae5; color:#059669; }
.badge-orange { background:#fef3c7; color:#d97706; }
.badge-red    { background:#fee2e2; color:#dc2626; }

/* ── Source pill ── */
.source-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f0f9ff; border: 1px solid #bae6fd;
    color: #0369a1; border-radius: 99px;
    padding: 4px 12px; font-size: 0.8rem; font-weight: 500;
    margin: 3px;
}

/* ── Divider ── */
.fancy-divider {
    height: 3px;
    background: linear-gradient(90deg,#6366f1,#8b5cf6,#ec4899);
    border-radius: 99px;
    margin: 24px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
PAGES = {
    "🏠  Home": "home",
    "📂  Upload Materials": "upload",
    "🔍  Ask Assistant": "ask",
    "📖  Explain Concept": "explain",
    "📝  Generate Quiz": "quiz",
    "💬  Chatbot": "chatbot",
    "📚  Knowledge Base": "knowledge_base",
}

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 8px 0;'>
        <div style='font-size:2.4rem;'>📡</div>
        <div style='font-weight:800; font-size:1.05rem; color:#e2e8f0; letter-spacing:0.3px;'>Telecom Assistant</div>
        <div style='font-size:0.75rem; color:#94a3b8; margin-top:2px;'>AI-Powered Learning</div>
    </div>
    <div style='height:1px; background:linear-gradient(90deg,transparent,#334155,transparent); margin:12px 0 16px 0;'></div>
    """, unsafe_allow_html=True)

    selected_label = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown("""
    <div style='height:1px; background:linear-gradient(90deg,transparent,#334155,transparent); margin:16px 0 12px 0;'></div>
    <div style='text-align:center; font-size:0.72rem; color:#64748b; padding-bottom:12px;'>
        Powered by Groq AI &amp; RAG<br>
        <span style='color:#475569;'>sentence-transformers · ChromaDB</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Route ────────────────────────────────────────────────────────────────────
page_key = PAGES[selected_label]

try:
    if page_key == "home":
        from ui.home import render
    elif page_key == "upload":
        from ui.upload import render
    elif page_key == "ask":
        from ui.ask import render
    elif page_key == "explain":
        from ui.explain import render
    elif page_key == "quiz":
        from ui.quiz import render
    elif page_key == "chatbot":
        from ui.chatbot import render
    elif page_key == "knowledge_base":
        from ui.knowledge_base import render
    else:
        def render():
            st.error(f"Unknown page: {page_key}")
    render()
except ImportError as exc:
    st.error(f"Import error: {exc}\n\nRun: `pip install -r requirements.txt`")
    st.exception(exc)
except Exception as exc:
    st.error(f"Page error: {exc}")
    st.exception(exc)
