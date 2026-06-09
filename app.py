"""
Clueless Consultant - AI Coaching Tool for Junior Consultants
Built with Claude. Architecture: Jazz Rasool's Social Vitamins (Support, Challenge, Reflection)
Run with: python -m streamlit run app.py
"""

import streamlit as st
import anthropic
import json
from datetime import datetime
from coach import SYSTEM_PROMPT, SCENARIOS, PROBLEM_TYPES

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Clueless Consultant",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Hero */
    .hero {
        padding: 2rem 0 1.5rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    .hero-tag {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.75rem;
        margin-bottom: 0.75rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.03em;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.4rem;
    }

    /* Scenario card */
    .scenario-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.75rem;
    }
    .scenario-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #f59e0b;
        margin-bottom: 0.75rem;
    }
    .scenario-text {
        font-size: 0.95rem;
        line-height: 1.75;
        color: #e2e8f0;
    }

    /* Input labels */
    .input-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.35rem;
        margin-top: 1.25rem;
    }

    /* Coaching vitamins */
    .vitamin-challenge {
        background: #fff7ed;
        border-left: 4px solid #f97316;
        border-radius: 0 10px 10px 0;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.85rem;
    }
    .vitamin-challenge-label {
        font-size: 0.62rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #c2410c;
        margin-bottom: 0.5rem;
    }
    .vitamin-challenge-text {
        color: #7c2d12;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    .vitamin-support {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        border-radius: 0 10px 10px 0;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.85rem;
    }
    .vitamin-support-label {
        font-size: 0.62rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #15803d;
        margin-bottom: 0.5rem;
    }
    .vitamin-support-text {
        color: #14532d;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    .vitamin-reflection {
        background: #eef2ff;
        border-left: 4px solid #6366f1;
        border-radius: 0 10px 10px 0;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.85rem;
    }
    .vitamin-reflection-label {
        font-size: 0.62rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #4338ca;
        margin-bottom: 0.5rem;
    }
    .vitamin-reflection-text {
        color: #1e1b4b;
        font-size: 1rem;
        line-height: 1.7;
        font-style: italic;
        font-weight: 500;
    }

    /* Ratio badge */
    .ratio-badge {
        display: inline-block;
        border-radius: 6px;
        padding: 0.2rem 0.65rem;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 1rem;
    }
    .ratio-heavy-challenge { background: #fee2e2; color: #991b1b; }
    .ratio-balanced        { background: #fef9c3; color: #854d0e; }
    .ratio-heavy-reflection{ background: #ede9fe; color: #5b21b6; }

    /* Divider */
    .thin-divider {
        border: none;
        border-top: 1px solid #f3f4f6;
        margin: 1.5rem 0;
    }

    /* Token info */
    .token-info {
        font-size: 0.72rem;
        color: #d1d5db;
        text-align: right;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "scenario_index" not in st.session_state:
    st.session_state.scenario_index = 0
if "result" not in st.session_state:
    st.session_state.result = None
if "final_message" not in st.session_state:
    st.session_state.final_message = None

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">AI Coach</div>
    <div class="hero-title">Clueless Consultant</div>
    <div class="hero-subtitle">
        You do the thinking. Claude tells you where you went wrong.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Scenario ──────────────────────────────────────────────────
scenario = SCENARIOS[st.session_state.scenario_index]

st.markdown(f"""
<div class="scenario-card">
    <div class="scenario-label">Client situation &nbsp;|&nbsp; {scenario['context']}</div>
    <div class="scenario-text">{scenario['text']}</div>
</div>
""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────
st.markdown('<div class="input-label">Your problem classification</div>', unsafe_allow_html=True)
classification = st.selectbox(
    "classification",
    PROBLEM_TYPES,
    label_visibility="collapsed"
)

st.markdown('<div class="input-label">Your leading hypothesis -- what do you think is actually going on?</div>', unsafe_allow_html=True)
hypothesis = st.text_area(
    "hypothesis",
    placeholder="State your hypothesis in 1-2 sentences. Be specific about cause, not symptom.",
    height=90,
    label_visibility="collapsed"
)

st.markdown('<div class="input-label">Your first diagnostic question -- what would you ask the client right now?</div>', unsafe_allow_html=True)
first_question = st.text_area(
    "first_question",
    placeholder="The single most important question you would ask before anything else.",
    height=75,
    label_visibility="collapsed"
)

# ── Buttons ───────────────────────────────────────────────────
col_submit, col_next, _ = st.columns([1.2, 1.2, 2])

valid = (
    classification != "Select a classification..." and
    bool(hypothesis.strip()) and
    bool(first_question.strip())
)

submit = col_submit.button("Get coached", type="primary", disabled=not valid)

def next_scenario():
    st.session_state.scenario_index = (st.session_state.scenario_index + 1) % len(SCENARIOS)
    st.session_state.result = None
    st.session_state.final_message = None

col_next.button("New scenario", on_click=next_scenario)

# ── Coaching ──────────────────────────────────────────────────
if submit and valid:
    user_response = (
        f"Scenario: {scenario['text']}\n\n"
        f"The junior consultant responded:\n"
        f"- Problem classification: {classification}\n"
        f"- Leading hypothesis: {hypothesis.strip()}\n"
        f"- First diagnostic question: {first_question.strip()}"
    )

    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else None
        client = anthropic.Anthropic(api_key=api_key)

        stream_box = st.empty()
        raw = ""

        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_response}]
        ) as stream:
            for text in stream.text_stream:
                raw += text
                stream_box.markdown(
                    f'<div style="font-family:monospace;font-size:0.75rem;color:#6b7280;'
                    f'background:#f9fafb;padding:1rem 1.25rem;border-radius:8px;'
                    f'border:1px solid #e5e7eb;white-space:pre-wrap;line-height:1.6;">'
                    f'Evaluating your response...\n{raw}&#9646;</div>',
                    unsafe_allow_html=True
                )
            final_msg = stream.get_final_message()

        stream_box.empty()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)
        st.session_state.result = data
        st.session_state.final_message = final_msg

    except json.JSONDecodeError as e:
        st.error(f"Claude returned unexpected output. Try again. ({e})")
        st.stop()
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

# ── Display result ────────────────────────────────────────────
if st.session_state.result:
    data = st.session_state.result
    final_msg = st.session_state.final_message

    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

    ratio = data.get("vitamin_ratio", "balanced")
    ratio_class_map = {
        "heavy_challenge":  "ratio-heavy-challenge",
        "balanced":         "ratio-balanced",
        "heavy_reflection": "ratio-heavy-reflection"
    }
    ratio_class = ratio_class_map.get(ratio, "ratio-balanced")
    ratio_label = ratio.replace("_", " ").title()

    st.markdown(
        f'<span class="ratio-badge {ratio_class}">{ratio_label}</span>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="vitamin-challenge">
        <div class="vitamin-challenge-label">Challenge</div>
        <div class="vitamin-challenge-text">{data['challenge']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vitamin-support">
        <div class="vitamin-support-label">Support</div>
        <div class="vitamin-support-text">{data['support']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vitamin-reflection">
        <div class="vitamin-reflection-label">Reflect on this</div>
        <div class="vitamin-reflection-text">{data['reflection_question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if final_msg:
        st.markdown(
            f'<div class="token-info">'
            f'{final_msg.usage.input_tokens} tokens in &nbsp;·&nbsp; '
            f'{final_msg.usage.output_tokens} out &nbsp;·&nbsp; '
            f'{datetime.now().strftime("%d %b %Y, %H:%M")}'
            f'</div>',
            unsafe_allow_html=True
        )
