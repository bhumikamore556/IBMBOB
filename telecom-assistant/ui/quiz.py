"""Quiz page — modern card-based quiz with visual score display."""
import streamlit as st
from services.quiz_service import generate_quiz, score_quiz
from models.granite_model import is_configured
from utils.helpers import TELECOM_TOPICS, build_score_badge, get_learning_recommendations


def render():
    st.markdown("""
    <div class="page-title">📝 Generate Quiz</div>
    <div class="page-subtitle">Test your telecom knowledge with AI-generated multiple-choice questions</div>
    """, unsafe_allow_html=True)

    if not is_configured():
        st.markdown("""
        <div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:12px;
                    padding:12px 16px; margin-bottom:12px;">
            ⚠️ <strong style="color:#92400e;">Groq API key not set</strong> — add GROQ_API_KEY to your .env file to generate quizzes.
        </div>
        """, unsafe_allow_html=True)

    # ── Session init ──────────────────────────────────────────────────
    for k, v in [("quiz_questions", []), ("quiz_answers", {}),
                  ("quiz_submitted", False), ("quiz_score_result", None),
                  ("quiz_topic", "")]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Route ─────────────────────────────────────────────────────────
    if not st.session_state.quiz_questions or st.session_state.quiz_submitted:
        _config_panel()
    else:
        _quiz_panel()


# ─────────────────────────────────────────────────────────────────────────────
def _config_panel():
    """Quiz configuration UI."""
    if st.session_state.quiz_score_result:
        _score_panel(st.session_state.quiz_score_result, st.session_state.quiz_topic)
        st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-blue">
        <div style="font-weight:700; color:#1e293b; font-size:1rem; margin-bottom:4px;">⚙️ Quiz Configuration</div>
        <div style="color:#64748b; font-size:0.87rem;">Choose your topic, difficulty level, and number of questions</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        topic_opt = st.selectbox("📡 Topic", ["Custom…"] + TELECOM_TOPICS, index=1)
        if topic_opt == "Custom…":
            topic = st.text_input("Custom topic", placeholder="e.g. mmWave, Carrier Aggregation…")
        else:
            topic = topic_opt

    with col2:
        difficulty = st.selectbox(
            "🎯 Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
            help="Easy=basics, Medium=application, Hard=advanced",
        )

    with col3:
        num_q = st.slider("🔢 Questions", 3, 15, 5)

    use_docs = st.checkbox(
        "📂 Use uploaded documents as quiz source",
        value=True,
        help="Grounds questions in your learning materials when available",
    )

    if st.button("🎯  Generate Quiz", type="primary", use_container_width=True,
                 disabled=not is_configured()):
        if not topic or not topic.strip():
            st.error("Please enter or select a topic.")
            return
        with st.spinner(f"Generating {num_q} {difficulty} questions on **{topic}**…"):
            try:
                qs = generate_quiz(topic=topic, num_questions=num_q,
                                   difficulty=difficulty, use_documents=use_docs)
                st.session_state.quiz_questions = qs
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score_result = None
                st.session_state.quiz_topic = topic
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Failed to generate quiz: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
def _quiz_panel():
    """Interactive quiz answering UI."""
    qs = st.session_state.quiz_questions
    topic = st.session_state.quiz_topic

    if st.session_state.quiz_submitted and st.session_state.quiz_score_result:
        _score_panel(st.session_state.quiz_score_result, topic)
        if st.button("🔄  New Quiz", type="secondary"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score_result = None
            st.rerun()
        return

    # Header bar
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff;
                border-radius:14px; padding:18px 24px; margin-bottom:20px;
                display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>
            <div style="font-weight:800; font-size:1.1rem;">📝 {topic}</div>
            <div style="opacity:0.8; font-size:0.85rem;">{len(qs)} questions</div>
        </div>
        <div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:8px 16px; font-size:0.88rem;">
            Answer all questions, then click Submit
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(qs):
            # Question card
            st.markdown(f"""
            <div style="background:#fafafa; border:1px solid #e2e8f0; border-radius:14px;
                        padding:18px 22px; margin-bottom:4px;">
                <div style="display:flex; align-items:flex-start; gap:10px;">
                    <span style="background:#6366f1; color:#fff; border-radius:8px;
                                 padding:3px 10px; font-size:0.8rem; font-weight:700;
                                 min-width:32px; text-align:center; margin-top:2px;">Q{i+1}</span>
                    <span style="font-weight:600; color:#1e293b; font-size:0.97rem; line-height:1.6;">{q['question']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            options_list = [f"{k}. {v}" for k, v in sorted(q["options"].items())]
            chosen = st.radio(
                f"ans_{i}",
                options=options_list,
                key=f"q_{i}",
                label_visibility="collapsed",
                horizontal=False,
            )
            answers[i] = chosen[0] if chosen else ""
            st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("✅  Submit Quiz", type="primary", use_container_width=True)

    if submitted:
        unanswered = [i + 1 for i, a in answers.items() if not a]
        if unanswered:
            st.warning(f"Please answer question(s): {unanswered}")
            return
        result = score_quiz(qs, answers)
        st.session_state.quiz_answers = answers
        st.session_state.quiz_submitted = True
        st.session_state.quiz_score_result = result
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
def _score_panel(result: dict, topic: str):
    """Visual score display with per-question breakdown."""
    pct = result["percentage"]
    badge = build_score_badge(pct)

    # Score hero
    if pct >= 80:
        bg = "linear-gradient(135deg,#10b981,#059669)"
    elif pct >= 60:
        bg = "linear-gradient(135deg,#f59e0b,#d97706)"
    elif pct >= 40:
        bg = "linear-gradient(135deg,#f97316,#ea580c)"
    else:
        bg = "linear-gradient(135deg,#ef4444,#dc2626)"

    st.markdown(f"""
    <div style="background:{bg}; color:#fff; border-radius:20px; padding:32px 40px;
                text-align:center; margin-bottom:20px;">
        <div style="font-size:3rem; font-weight:900;">{pct}%</div>
        <div style="font-size:1.5rem; font-weight:700; margin:4px 0;">{badge}</div>
        <div style="opacity:0.9; font-size:0.95rem; margin-top:8px;">
            {result['correct']} correct · {result['incorrect']} incorrect · {result['total']} total
        </div>
        <div style="margin-top:14px; display:flex; justify-content:center; gap:24px; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:8px 20px;">
                <div style="font-size:1.5rem; font-weight:800;">{result['correct']}</div>
                <div style="font-size:0.78rem; opacity:0.85;">✅ Correct</div>
            </div>
            <div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:8px 20px;">
                <div style="font-size:1.5rem; font-weight:800;">{result['incorrect']}</div>
                <div style="font-size:0.78rem; opacity:0.85;">❌ Incorrect</div>
            </div>
            <div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:8px 20px;">
                <div style="font-size:1.5rem; font-weight:800;">{result['total']}</div>
                <div style="font-size:0.78rem; opacity:0.85;">📝 Questions</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Per-question breakdown
    st.markdown("""
    <h3 style="font-weight:700; color:#1e293b; font-size:1.05rem; margin:16px 0 10px 0;">
        📋 Question Breakdown
    </h3>
    """, unsafe_allow_html=True)

    for i, r in enumerate(result["results"]):
        icon = "✅" if r["is_correct"] else "❌"
        border = "#10b981" if r["is_correct"] else "#ef4444"
        bg_col = "#f0fdf4" if r["is_correct"] else "#fef2f2"

        q_short = r["question"][:90] + ("…" if len(r["question"]) > 90 else "")
        with st.expander(f"{icon} Q{i+1}: {q_short}"):
            st.markdown(f"""
            <div style="background:{bg_col}; border-left:4px solid {border}; border-radius:10px;
                        padding:14px 18px; font-size:0.9rem;">
                <div style="margin-bottom:6px;">
                    <strong>Your answer:</strong> {r['user_answer']}. {r['options'].get(r['user_answer'], 'N/A')}
                </div>
                <div style="margin-bottom:6px;">
                    <strong>Correct answer:</strong> {r['correct_answer']}. {r['options'].get(r['correct_answer'], 'N/A')}
                </div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px solid rgba(0,0,0,0.06); color:#475569;">
                    📖 <em>{r['explanation']}</em>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recommendations
    st.markdown("""<div class="fancy-divider"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <h3 style="font-weight:700; color:#1e293b; font-size:1.05rem; margin-bottom:10px;">
        📚 Study Recommendations
    </h3>
    """, unsafe_allow_html=True)
    incorrect = [r for r in result["results"] if not r["is_correct"]]
    rec = get_learning_recommendations(incorrect)
    st.markdown(f"""
    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:12px;
                padding:16px 20px; color:#0369a1; font-size:0.9rem; white-space:pre-wrap;">
{rec}
    </div>
    """, unsafe_allow_html=True)
