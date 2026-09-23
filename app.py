"""
Clueless Consultant - AI Coaching Tool for Junior Consultants
Built with Claude. Architecture: Jazz Rasool's Social Vitamins (Support, Challenge, Reflection)
Run with: python -m streamlit run app.py
"""

import streamlit as st
import anthropic
import html
import json
import re
from datetime import datetime
from coach import build_system_prompt, SCENARIOS, PROBLEM_TYPES, PROBLEM_TYPE_LABELS, SCENARIO_KB_IDS, SCENARIO_FRAMEWORK
from kb_lookup import load_kb, get_by_ids, match_by_keywords
from model_answer import MODEL_ANSWER_SYSTEM_PROMPT, build_model_answer_prompt

UI_TEXT = {
    "en": {
        "hero_tag": "AI Coach",
        "hero_title": "Clueless Consultant",
        "hero_subtitle": "You do the thinking. Claude tells you where you went wrong.",
        "scenario_label": "Client situation",
        "mode_label": "How do you want to practice?",
        "mode_scenario": "Pick a scenario",
        "mode_custom": "Paste your own problem",
        "custom_label": "Client problem statement",
        "custom_placeholder": "Type or paste what the client says. Messy, emotional, incomplete is fine.",
        "reveal_button": "Reveal model answer",
        "classification_label": "Your problem classification",
        "hypothesis_label": "Your leading hypothesis -- what do you think is actually going on?",
        "hypothesis_placeholder": "State your hypothesis in 1-2 sentences. Be specific about cause, not symptom.",
        "question_label": "Your first diagnostic question -- what would you ask the client right now?",
        "question_placeholder": "The single most important question you would ask before anything else.",
        "recommendation_label": "Your recommendation -- if your hypothesis holds, what would you actually tell the client to do?",
        "recommendation_placeholder": "State your recommendation in 1-2 sentences. Short-term vs. medium-term if it matters. Commit to a position.",
        "submit_button": "Get coached",
        "next_button": "New scenario",
        "framework_note": (
            "Social Vitamins framework &nbsp;|&nbsp; Jazz Rasool &nbsp;|&nbsp; "
            "Support &nbsp;· &nbsp;Challenge &nbsp;·&nbsp; Reflection"
        ),
        "challenge_label": "Challenge",
        "support_label": "Support",
        "reflection_label": "Reflect on this",
        "ratio_labels": {
            "heavy_challenge": "Heavy Challenge",
            "balanced": "Balanced",
            "heavy_reflection": "Heavy Reflection",
        },
        "tokens_in": "tokens in",
        "tokens_out": "out",
        "json_error": "Claude returned unexpected output. Try again.",
        "generic_error": "Something went wrong:",
        "hint_ready": "All four answered. Ready when you are.",
        "hint_missing": "Still needed:",
        "brand_line": "Case practice",
        "hero_method": "Social Vitamins method",
        "case_label": "Case",
        "answer_heading": "Your answer",
        "coach_heading": "Coach's notes",
        "model_heading": "Model answer",
        "evaluating": "Reading your answer...",
    },
    "de": {
        "hero_tag": "KI-Coach",
        "hero_title": "Clueless Consultant",
        "hero_subtitle": "Du denkst. Claude sagt dir, wo du falsch liegst.",
        "scenario_label": "Kundensituation",
        "mode_label": "Wie möchtest du üben?",
        "mode_scenario": "Szenario wählen",
        "mode_custom": "Eigenes Problem einfügen",
        "custom_label": "Kundenproblem",
        "custom_placeholder": "Formuliere oder füge ein, was der Kunde sagt. Chaotisch, emotional, unvollständig ist okay.",
        "reveal_button": "Musterlösung anzeigen",
        "classification_label": "Deine Problemklassifikation",
        "hypothesis_label": "Deine Leithypothese -- was, glaubst du, steckt wirklich dahinter?",
        "hypothesis_placeholder": "Formuliere deine Hypothese in 1-2 Sätzen. Konkret zur Ursache, nicht zum Symptom.",
        "question_label": "Deine erste diagnostische Frage -- was würdest du den Kunden jetzt sofort fragen?",
        "question_placeholder": "Die eine wichtigste Frage, die du vor allem anderen stellen würdest.",
        "recommendation_label": "Deine Empfehlung -- wenn deine Hypothese stimmt, was würdest du dem Kunden konkret raten?",
        "recommendation_placeholder": "Formuliere deine Empfehlung in 1-2 Sätzen. Kurzfristig vs. mittelfristig, wenn relevant. Beziehe klar Stellung.",
        "submit_button": "Coaching erhalten",
        "next_button": "Neues Szenario",
        "framework_note": (
            "Social-Vitamins-Framework &nbsp;|&nbsp; Jazz Rasool &nbsp;|&nbsp; "
            "Support &nbsp;· &nbsp;Challenge &nbsp;·&nbsp; Reflexion"
        ),
        "challenge_label": "Challenge",
        "support_label": "Support",
        "reflection_label": "Zum Nachdenken",
        "ratio_labels": {
            "heavy_challenge": "Starker Challenge",
            "balanced": "Ausgewogen",
            "heavy_reflection": "Starke Reflexion",
        },
        "tokens_in": "Tokens rein",
        "tokens_out": "raus",
        "json_error": "Claude hat unerwarteten Output geliefert. Nochmal versuchen.",
        "generic_error": "Etwas ist schiefgelaufen:",
        "hint_ready": "Alle vier beantwortet. Bereit, wenn du es bist.",
        "hint_missing": "Noch offen:",
        "brand_line": "Case-Training",
        "hero_method": "Social-Vitamins-Methode",
        "case_label": "Fall",
        "answer_heading": "Deine Antwort",
        "coach_heading": "Anmerkungen des Coaches",
        "model_heading": "Musterlösung",
        "evaluating": "Deine Antwort wird gelesen...",
    },
}

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Clueless Consultant",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────
# Palette rationale: deep navy base (trust, calm, approach mindset for open-ended
# thinking). No red anywhere - the challenge is blunt in words, not in color,
# to keep psychological safety intact. Amber is the single warm accent (action).
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --paper: #f6f3ec;
        --paper-deep: #ece6da;
        --card: #fffdf8;
        --ink: #0f1f3d;
        --ink-soft: #33415e;
        --muted: #6a7489;
        --faint: #a3aaba;
        --rule: #dcd5c7;
        --navy: #1b2f5b;
        --blue: #2f5fb3;
        --blue-soft: #e8eef9;
        --sky: #f1f5fc;
        --green: #2d6a4f;
        --green-soft: #ebf3ee;
        --amber: #e7a13a;
        --amber-deep: #b87512;
        --amber-soft: #fbf0dc;
        --serif: 'Fraunces', Georgia, serif;
        --sans: 'IBM Plex Sans', 'Segoe UI', sans-serif;
        --mono: 'IBM Plex Mono', ui-monospace, monospace;
    }

    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"] {display: none !important;}
    header[data-testid="stHeader"] {background: transparent;}

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--paper) !important;
    }
    html, body, .stApp, .stMarkdown, p, textarea, input, button, label {
        font-family: var(--sans);
    }
    .stApp { color: var(--ink); }
    .stApp p, .stApp label, .stApp textarea, .stApp input, .stApp button,
    .stApp [data-baseweb="select"] { font-family: var(--sans) !important; }

    .block-container {
        max-width: 780px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    @keyframes fadeRise {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 0.3; transform: scale(0.85); }
        50% { opacity: 1; transform: scale(1); }
    }
    @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
    }

    /* ── Masthead ───────────────────────────────────────────── */
    .masthead {
        font-family: var(--mono);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--navy);
        padding-top: 0.55rem;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .masthead .mark {
        width: 9px; height: 9px; background: var(--navy); flex: none;
        box-shadow: 4px 4px 0 var(--amber);
    }

    /* ── Hero ───────────────────────────────────────────────── */
    .hero {
        padding: 2.6rem 0 2rem 0;
        border-bottom: 1px solid var(--rule);
        margin-bottom: 2rem;
        animation: fadeRise 0.5s ease both;
    }
    .hero-tag {
        font-family: var(--mono);
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.9rem;
    }
    .hero-tag b { color: var(--amber-deep); font-weight: 600; }
    .hero-title {
        font-family: var(--serif);
        font-size: clamp(2.4rem, 7vw, 3.6rem);
        font-weight: 600;
        line-height: 1.02;
        color: var(--ink);
        letter-spacing: -0.025em;
        margin: 0;
    }
    .hero-title em {
        font-style: italic;
        font-weight: 400;
        color: var(--blue);
    }
    .hero-subtitle {
        font-size: 1.08rem;
        color: var(--ink-soft);
        margin-top: 0.9rem;
        max-width: 34rem;
        line-height: 1.55;
    }

    /* ── Section headings ───────────────────────────────────── */
    .section-head {
        display: flex; align-items: baseline; gap: 0.75rem;
        margin: 2.4rem 0 0.6rem 0;
    }
    .section-head .t {
        font-family: var(--serif);
        font-size: 1.45rem;
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -0.01em;
        white-space: nowrap;
    }
    .section-head .line {
        flex: 1; height: 1px; background: var(--rule); transform: translateY(-0.3rem);
    }

    /* ── Labels ─────────────────────────────────────────────── */
    .input-label {
        display: flex; align-items: baseline; gap: 0.7rem;
        margin: 1.6rem 0 0.45rem 0;
        font-size: 0.95rem;
        color: var(--ink);
        line-height: 1.4;
    }
    .input-label.plain {
        font-family: var(--mono);
        font-size: 0.7rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase;
        color: var(--muted);
        margin-top: 0.5rem;
    }
    .input-label .step-num {
        font-family: var(--mono);
        font-size: 0.72rem; font-weight: 600;
        color: var(--amber-deep);
        flex: none;
        min-width: 1.4rem;
    }
    .input-label .main { font-weight: 600; display: block; }
    .input-label .sub { color: var(--muted); font-weight: 400; font-size: 0.86rem; display: block; margin-top: 0.1rem; }

    /* ── Client brief (scenario card) ───────────────────────── */
    .scenario-card {
        position: relative;
        background: var(--navy);
        border-radius: 4px;
        padding: 1.6rem 1.9rem 1.8rem 1.9rem;
        margin: 1.1rem 0 0.5rem 0;
        box-shadow: 8px 8px 0 var(--paper-deep);
        animation: fadeRise 0.5s ease 0.05s both;
    }
    .scenario-meta {
        display: flex; justify-content: space-between; align-items: baseline; gap: 1rem;
        font-family: var(--mono);
        font-size: 0.66rem; font-weight: 600;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: #9fb4dc;
        padding-bottom: 0.9rem;
        margin-bottom: 1.1rem;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }
    .scenario-meta .ctx { color: var(--amber); }
    .scenario-text {
        font-family: var(--serif);
        font-size: 1.14rem;
        line-height: 1.62;
        color: #f3f1ea;
        font-weight: 400;
    }
    .scenario-text::before {
        content: "\\201C";
        font-family: var(--serif);
        color: var(--amber);
        font-size: 2.6rem;
        line-height: 0;
        vertical-align: -0.9rem;
        margin-right: 0.2rem;
    }

    /* ── Segmented pill radios ──────────────────────────────── */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 0.25rem !important;
        background: var(--card);
        border: 1px solid var(--rule);
        border-radius: 999px;
        padding: 3px;
        display: inline-flex !important;
        flex-wrap: nowrap !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        border-radius: 999px;
        padding: 0.38rem 0.95rem;
        margin: 0 !important;
        transition: background 0.15s ease;
        cursor: pointer;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover { background: var(--sky); }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) { background: var(--navy); }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display: none; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.84rem; font-weight: 500; color: var(--ink-soft); margin: 0;
        white-space: nowrap;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) [data-testid="stMarkdownContainer"] p {
        color: #ffffff; font-weight: 600;
    }
    .st-key-language { align-self: flex-end; margin-left: auto; }

    /* ── Inputs ─────────────────────────────────────────────── */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"] {
        background: var(--card) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"] {
        border: 1px solid var(--rule) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stTextArea"] textarea {
        background: var(--card) !important;
        color: var(--ink) !important;
        font-size: 0.95rem !important;
        line-height: 1.55 !important;
    }
    div[data-testid="stTextArea"] textarea::placeholder { color: var(--faint) !important; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"]:hover {
        border-color: #bfb6a4 !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div,
    div[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(47,95,179,0.16) !important;
    }

    /* ── Buttons ────────────────────────────────────────────── */
    button[data-testid="stBaseButton-primary"],
    button[data-testid="stBaseButton-secondary"] {
        border-radius: 4px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.3rem !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease !important;
    }
    button[data-testid="stBaseButton-primary"] {
        background: var(--amber) !important;
        border: 1px solid var(--amber) !important;
        color: var(--ink) !important;
        box-shadow: 3px 3px 0 var(--navy);
    }
    button[data-testid="stBaseButton-primary"] p { color: var(--ink) !important; font-weight: 700 !important; }
    button[data-testid="stBaseButton-primary"]:not(:disabled):hover {
        transform: translate(-1px, -1px);
        box-shadow: 4px 4px 0 var(--navy);
    }
    button[data-testid="stBaseButton-primary"]:not(:disabled):active {
        transform: translate(2px, 2px);
        box-shadow: 1px 1px 0 var(--navy);
    }
    button[data-testid="stBaseButton-primary"]:disabled {
        background: var(--paper-deep) !important;
        border-color: var(--rule) !important;
        box-shadow: none;
        cursor: not-allowed !important;
    }
    button[data-testid="stBaseButton-primary"]:disabled p { color: var(--faint) !important; }
    button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: 1px solid var(--navy) !important;
        color: var(--navy) !important;
    }
    button[data-testid="stBaseButton-secondary"] p { color: var(--navy) !important; }
    button[data-testid="stBaseButton-secondary"]:not(:disabled):hover {
        background: var(--navy) !important;
    }
    button[data-testid="stBaseButton-secondary"]:not(:disabled):hover p { color: #fff !important; }
    button:focus-visible { outline: 2px solid var(--blue) !important; outline-offset: 2px; }

    .validation-hint {
        font-size: 0.8rem; color: var(--muted); margin-top: 0.7rem;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .validation-hint .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--amber); flex: none; }
    .validation-hint.ready { color: var(--green); font-weight: 500; }
    .validation-hint.ready .dot { background: var(--green); }

    /* ── Streaming box ──────────────────────────────────────── */
    .stream-box {
        font-family: var(--mono);
        font-size: 0.74rem;
        color: var(--muted);
        background: var(--card);
        border: 1px dashed var(--rule);
        border-radius: 4px;
        padding: 1rem 1.25rem;
        white-space: pre-wrap;
        line-height: 1.6;
        margin-top: 1.5rem;
    }
    .stream-box .head { color: var(--navy); font-weight: 600; }
    .thinking-dot {
        display: inline-block; width: 6px; height: 6px; border-radius: 50%;
        background: var(--blue); margin-right: 8px; vertical-align: middle;
        animation: pulseDot 1.1s ease-in-out infinite;
    }

    /* ── Coach's notes (Social Vitamins) ────────────────────── */
    .result-meta {
        display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem;
        margin-bottom: 1.2rem;
    }
    .ratio-badge {
        font-family: var(--mono);
        border-radius: 3px;
        padding: 0.22rem 0.6rem;
        font-size: 0.66rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em;
    }
    .ratio-heavy-challenge  { background: var(--navy); color: #fff; }
    .ratio-balanced         { background: var(--blue-soft); color: var(--navy); }
    .ratio-heavy-reflection { background: var(--sky); color: var(--blue); border: 1px solid #cbd8f0; }
    .framework-note { font-size: 0.72rem; color: var(--muted); }

    .vitamin {
        position: relative;
        border-radius: 4px;
        padding: 1.2rem 1.4rem 1.25rem 1.4rem;
        margin-bottom: 0.9rem;
        animation: fadeRise 0.45s ease both;
    }
    .vitamin-label {
        font-family: var(--mono);
        font-size: 0.66rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.14em;
        margin-bottom: 0.55rem;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .vitamin-label .n { opacity: 0.55; }
    .vitamin-text { font-size: 0.98rem; line-height: 1.68; }

    .vitamin-challenge {
        background: var(--card);
        border: 1px solid var(--rule);
        border-left: 5px solid var(--navy);
    }
    .vitamin-challenge .vitamin-label { color: var(--navy); }
    .vitamin-challenge .vitamin-text { color: var(--ink); font-weight: 500; }

    .vitamin-support {
        background: var(--green-soft);
        border-left: 5px solid var(--green);
        animation-delay: 0.08s;
    }
    .vitamin-support .vitamin-label { color: var(--green); }
    .vitamin-support .vitamin-text { color: #1f3d30; }

    .vitamin-reflection {
        background: var(--sky);
        border: 1px solid #d3def2;
        padding: 1.5rem 1.6rem;
        animation-delay: 0.16s;
    }
    .vitamin-reflection .vitamin-label { color: var(--blue); }
    .vitamin-reflection .vitamin-text {
        font-family: var(--serif);
        font-style: italic;
        font-size: 1.28rem;
        line-height: 1.45;
        color: var(--navy);
    }

    .token-info {
        font-family: var(--mono);
        font-size: 0.66rem;
        color: var(--faint);
        text-align: right;
        margin-top: 0.4rem;
    }

    /* ── Model answer ───────────────────────────────────────── */
    .model-framework-badge {
        display: inline-block;
        font-family: var(--mono);
        border-radius: 3px;
        padding: 0.25rem 0.7rem;
        font-weight: 600;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0.4rem 0 0.6rem 0;
        background: var(--navy);
        color: #fff;
    }
    .model-step-label {
        font-family: var(--serif);
        font-size: 1.12rem;
        font-weight: 600;
        color: var(--navy);
        margin: 1.6rem 0 0.55rem 0;
        padding-top: 0.9rem;
        border-top: 1px solid var(--rule);
    }
    .model-step-label.flags { color: var(--amber-deep); }
    .model-hyp-item, .model-q-item {
        background: var(--card);
        border: 1px solid var(--rule);
        border-left: 3px solid var(--blue);
        border-radius: 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.92rem;
        color: var(--ink);
        line-height: 1.55;
    }
    .model-hyp-evidence, .model-q-reveals {
        color: var(--muted);
        font-size: 0.84rem;
        margin-top: 0.3rem;
    }
    .model-flag-item {
        background: var(--amber-soft);
        border-left: 3px solid var(--amber);
        border-radius: 4px;
        padding: 0.65rem 1rem;
        margin-bottom: 0.45rem;
        color: #5a3a08;
        font-size: 0.9rem;
    }
    .branch-title {
        font-weight: 600;
        color: var(--ink);
        font-size: 0.93rem;
        margin-top: 0.7rem;
    }
    .branch-item {
        color: var(--ink-soft);
        font-size: 0.88rem;
        padding-left: 1rem;
        margin-top: 0.25rem;
        line-height: 1.5;
    }

    .card {
        background: var(--card);
        border: 1px solid var(--rule);
        border-radius: 4px;
        padding: 1.25rem 1.5rem;
        margin: 0.8rem 0 1rem 0;
    }
    .card-title {
        font-family: var(--mono);
        font-size: 0.66rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 0.5rem;
    }
    .ws-format { font-weight: 600; color: var(--ink); }
    .ws-duration { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.6rem; }
    .ws-output {
        margin-top: 0.8rem; font-size: 0.88rem;
        background: var(--green-soft); border-radius: 3px;
        padding: 0.55rem 0.8rem; color: #1f3d30;
    }

    .stApp .stMarkdown p, .stApp .stMarkdown li { color: var(--ink); line-height: 1.6; }

    @media (max-width: 640px) {
        .scenario-card { padding: 1.3rem 1.2rem 1.4rem 1.2rem; box-shadow: 5px 5px 0 var(--paper-deep); }
        .scenario-meta { flex-direction: column; gap: 0.3rem; }
        .scenario-text { font-size: 1.04rem; }
        .vitamin-reflection .vitamin-text { font-size: 1.14rem; }
        .st-key-language { align-self: flex-start; margin-left: 0; }
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
if "language" not in st.session_state:
    st.session_state.language = "en"
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "scenario"
if "model_answer" not in st.session_state:
    st.session_state.model_answer = None

kb_entries = load_kb()

def reset_coaching_state():
    st.session_state.result = None
    st.session_state.final_message = None
    st.session_state.model_answer = None

def label_html(text, step=None):
    """Split 'Main label -- helper text' into a bold main part and a muted helper."""
    main, _, sub = text.partition(" -- ")
    num = f'<span class="step-num">{step:02d}</span>' if step else ""
    sub_html = f' <span class="sub">{sub}</span>' if sub else ""
    return f'<div class="input-label">{num}<div><span class="main">{main}</span>{sub_html}</div></div>'

def section_head(title):
    st.markdown(f'<div class="section-head"><span class="t">{title}</span><span class="line"></span></div>', unsafe_allow_html=True)

# ── Masthead + language toggle ───────────────────────────────
col_brand, col_lang = st.columns([3, 2], vertical_alignment="center")
col_lang.radio(
    "Language",
    options=["en", "de"],
    format_func=lambda code: "English" if code == "en" else "Deutsch",
    horizontal=True,
    key="language",
    label_visibility="collapsed",
    on_change=reset_coaching_state,
)
lang = st.session_state.language
ui = UI_TEXT[lang]
col_brand.markdown(
    f'<div class="masthead"><span class="mark"></span>Clueless Consultant &nbsp;/&nbsp; {ui["brand_line"]}</div>',
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-tag"><b>{ui['hero_tag']}</b> &nbsp;·&nbsp; {ui['hero_method']}</div>
    <div class="hero-title"><em>Clueless</em> Consultant</div>
    <div class="hero-subtitle">
        {ui['hero_subtitle']}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input mode toggle ────────────────────────────────────────
st.markdown(f'<div class="input-label plain">{ui["mode_label"]}</div>', unsafe_allow_html=True)
st.radio(
    "input_mode",
    options=["scenario", "custom"],
    format_func=lambda m: ui["mode_scenario"] if m == "scenario" else ui["mode_custom"],
    horizontal=True,
    key="input_mode",
    label_visibility="collapsed",
    on_change=reset_coaching_state,
)

# ── Scenario or custom problem ───────────────────────────────
scenario = None
custom_problem = ""

if st.session_state.input_mode == "scenario":
    scenario = SCENARIOS[st.session_state.scenario_index]
    st.markdown(f"""
    <div class="scenario-card">
        <div class="scenario-meta">
            <span>{ui['scenario_label']} &nbsp;/&nbsp; <span class="ctx">{scenario['context'][lang]}</span></span>
            <span>{ui['case_label']} {st.session_state.scenario_index + 1:02d} / {len(SCENARIOS):02d}</span>
        </div>
        <div class="scenario-text">{scenario['text'][lang]}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(label_html(ui["custom_label"]), unsafe_allow_html=True)
    custom_problem = st.text_area(
        "custom_problem",
        placeholder=ui["custom_placeholder"],
        height=110,
        label_visibility="collapsed",
        key="custom_problem",
    )

# ── Inputs ────────────────────────────────────────────────────
section_head(ui["answer_heading"])
st.markdown(label_html(ui["classification_label"], step=1), unsafe_allow_html=True)
classification = st.selectbox(
    "classification",
    PROBLEM_TYPES,
    format_func=lambda key: PROBLEM_TYPE_LABELS[lang][key],
    label_visibility="collapsed"
)

st.markdown(label_html(ui["hypothesis_label"], step=2), unsafe_allow_html=True)
hypothesis = st.text_area(
    "hypothesis",
    placeholder=ui["hypothesis_placeholder"],
    height=90,
    label_visibility="collapsed"
)

st.markdown(label_html(ui["question_label"], step=3), unsafe_allow_html=True)
first_question = st.text_area(
    "first_question",
    placeholder=ui["question_placeholder"],
    height=75,
    label_visibility="collapsed"
)

st.markdown(label_html(ui["recommendation_label"], step=4), unsafe_allow_html=True)
recommendation = st.text_area(
    "recommendation",
    placeholder=ui["recommendation_placeholder"],
    height=75,
    label_visibility="collapsed"
)

# ── Buttons ───────────────────────────────────────────────────
col_submit, col_next, _ = st.columns([1, 1.1, 2.6], gap="small")

situation_text = scenario["text"][lang] if st.session_state.input_mode == "scenario" else custom_problem.strip()

valid = (
    bool(situation_text) and
    classification != "select" and
    bool(hypothesis.strip()) and
    bool(first_question.strip()) and
    bool(recommendation.strip())
)

submit = col_submit.button(ui["submit_button"], type="primary", disabled=not valid)

def next_scenario():
    st.session_state.scenario_index = (st.session_state.scenario_index + 1) % len(SCENARIOS)
    reset_coaching_state()

if st.session_state.input_mode == "scenario":
    col_next.button(ui["next_button"], on_click=next_scenario)

missing = []
if classification == "select":
    missing.append(ui["classification_label"])
if not hypothesis.strip():
    missing.append(ui["hypothesis_label"].split(" -- ")[0])
if not first_question.strip():
    missing.append(ui["question_label"].split(" -- ")[0])
if not recommendation.strip():
    missing.append(ui["recommendation_label"].split(" -- ")[0])

if valid:
    st.markdown(f'<div class="validation-hint ready"><span class="dot"></span>{ui["hint_ready"]}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="validation-hint"><span class="dot"></span>{ui["hint_missing"]} {" · ".join(missing)}</div>', unsafe_allow_html=True)

# ── Coaching ──────────────────────────────────────────────────
if submit and valid:
    st.session_state.model_answer = None

    if st.session_state.input_mode == "scenario":
        kb_context = get_by_ids(SCENARIO_KB_IDS.get(scenario["id"], []), kb_entries)
    else:
        kb_context = match_by_keywords(situation_text, kb_entries, entry_types=["competency_pattern", "research_finding", "junior_pitfall"], limit=3)

    user_response = (
        f"Scenario: {situation_text}\n\n"
        f"The junior consultant responded:\n"
        f"- Problem classification: {PROBLEM_TYPE_LABELS['en'][classification]}\n"
        f"- Leading hypothesis: {hypothesis.strip()}\n"
        f"- First diagnostic question: {first_question.strip()}\n"
        f"- Recommendation: {recommendation.strip()}"
    )

    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else None
        client = anthropic.Anthropic(api_key=api_key)

        stream_box = st.empty()
        raw = ""

        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=build_system_prompt(lang, kb_context=kb_context),
            messages=[{"role": "user", "content": user_response}]
        ) as stream:
            for chunk in stream.text_stream:
                raw += chunk
                stream_box.markdown(
                    f'<div class="stream-box"><span class="head"><span class="thinking-dot"></span>'
                    f'{ui["evaluating"]}</span>\n{html.escape(raw)}&#9646;</div>',
                    unsafe_allow_html=True
                )
            final_msg = stream.get_final_message()

        stream_box.empty()

        # Robustly extract JSON -- find the outermost { } block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group()
        data = json.loads(raw)
        st.session_state.result = data
        st.session_state.final_message = final_msg

    except json.JSONDecodeError as e:
        st.error(f"{ui['json_error']} ({e})")
        st.stop()
    except Exception as e:
        st.error(f"{ui['generic_error']} {e}")
        st.stop()

# ── Display result ────────────────────────────────────────────
if st.session_state.result:
    data = st.session_state.result
    final_msg = st.session_state.final_message

    section_head(ui["coach_heading"])

    ratio = data.get("vitamin_ratio", "balanced")
    ratio_class_map = {
        "heavy_challenge":  "ratio-heavy-challenge",
        "balanced":         "ratio-balanced",
        "heavy_reflection": "ratio-heavy-reflection"
    }
    ratio_class = ratio_class_map.get(ratio, "ratio-balanced")
    ratio_label = ui["ratio_labels"].get(ratio, ui["ratio_labels"]["balanced"])

    st.markdown(
        f'<div class="result-meta"><span class="ratio-badge {ratio_class}">{ratio_label}</span>'
        f'<span class="framework-note">{ui["framework_note"]}</span></div>',
        unsafe_allow_html=True
    )

    for n, (kind, label_key, data_key) in enumerate([
        ("challenge", "challenge_label", "challenge"),
        ("support", "support_label", "support"),
        ("reflection", "reflection_label", "reflection_question"),
    ], start=1):
        st.markdown(f"""
        <div class="vitamin vitamin-{kind}">
            <div class="vitamin-label"><span class="n">{n:02d}</span>{ui[label_key]}</div>
            <div class="vitamin-text">{data[data_key]}</div>
        </div>
        """, unsafe_allow_html=True)

    if final_msg:
        st.markdown(
            f'<div class="token-info">'
            f'{final_msg.usage.input_tokens} {ui["tokens_in"]} &nbsp;·&nbsp; '
            f'{final_msg.usage.output_tokens} {ui["tokens_out"]} &nbsp;·&nbsp; '
            f'{datetime.now().strftime("%d %b %Y, %H:%M")}'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Reveal model answer ──────────────────────────────────────
    section_head(ui["model_heading"])
    reveal = st.button(ui["reveal_button"])

    if reveal:
        if st.session_state.input_mode == "scenario":
            model_kb_context = get_by_ids(SCENARIO_KB_IDS.get(scenario["id"], []), kb_entries)
            model_framework_hint = {"framework-diagnostic": "diagnostic", "framework-adoption": "adoption"}.get(
                SCENARIO_FRAMEWORK.get(scenario["id"])
            )
        else:
            model_kb_context = match_by_keywords(situation_text, kb_entries, entry_types=["competency_pattern", "research_finding"], limit=3)
            model_framework_hint = None

        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else None
            client = anthropic.Anthropic(api_key=api_key)

            model_response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2048,
                system=MODEL_ANSWER_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": build_model_answer_prompt(situation_text, kb_context=model_kb_context, framework_hint=model_framework_hint),
                }],
            )
            raw_model = model_response.content[0].text.strip()
            match_json = re.search(r'\{.*\}', raw_model, re.DOTALL)
            if match_json:
                raw_model = match_json.group()
            st.session_state.model_answer = json.loads(raw_model)
        except Exception as e:
            st.error(f"{ui['generic_error']} {e}")

    if st.session_state.model_answer:
        ma = st.session_state.model_answer
        try:
            framework_label = "Diagnostic method" if ma["framework_used"] == "diagnostic" else "Adoption method"
            st.markdown(f'<span class="model-framework-badge">{framework_label}</span>', unsafe_allow_html=True)

            if ma["framework_used"] == "diagnostic":
                st.markdown('<div class="model-step-label">Klären</div>', unsafe_allow_html=True)
                st.markdown(ma["klaeren"]["restated_problem"])
                for assumption in ma["klaeren"]["clarifying_assumptions"]:
                    st.markdown(f"- {assumption}")

                st.markdown('<div class="model-step-label">Strukturieren</div>', unsafe_allow_html=True)
                st.markdown(f"Root: {ma['strukturieren']['root_problem']}")
                for branch in ma["strukturieren"]["branches"]:
                    st.markdown(f'<div class="branch-title">↳ {branch["area"]}</div>', unsafe_allow_html=True)
                    for sub in branch["sub_issues"]:
                        st.markdown(f'<div class="branch-item">· {sub}</div>', unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Hypothese</div>', unsafe_allow_html=True)
                for h in ma["hypothese"]:
                    st.markdown(f"""
                    <div class="model-hyp-item">
                        {h['hypothesis']}
                        <div class="model-hyp-evidence">Evidence: {h['evidence']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Analysieren</div>', unsafe_allow_html=True)
                for q in ma["analysieren"]["diagnostic_questions"]:
                    st.markdown(f"""
                    <div class="model-q-item">
                        {q['question']}
                        <div class="model-q-reveals">Reveals: {q['what_it_reveals']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Synthetisieren</div>', unsafe_allow_html=True)
                st.markdown(ma["synthetisieren"]["recommendation"])
                ws = ma["synthetisieren"]["first_workshop"]
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Suggested first workshop</div>
                    <div class="ws-format">{ws['format']}</div>
                    <div class="ws-duration">{ws['duration']}</div>
                    {''.join(f'<div class="branch-item">· {item}</div>' for item in ws['agenda'])}
                    <div class="ws-output">
                        <strong>Output:</strong> {ws['key_output']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="model-step-label">Ist-Analyse</div>', unsafe_allow_html=True)
                for dim, val in ma["ist_analyse"].items():
                    st.markdown(f'<div class="branch-item">· <strong>{dim.replace("_", " ").title()}:</strong> {val}</div>', unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Zielbild</div>', unsafe_allow_html=True)
                st.markdown(ma["zielbild"])

                st.markdown('<div class="model-step-label">Gap-Analyse</div>', unsafe_allow_html=True)
                for gap in ma["gap_analyse"]:
                    st.markdown(f'<div class="branch-item">· {gap}</div>', unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Operationalisieren</div>', unsafe_allow_html=True)
                for ws in ma["operationalisieren"]:
                    st.markdown(f"""
                    <div class="model-hyp-item">
                        <strong>{ws['workstream']}</strong>
                        <div class="model-hyp-evidence">{ws['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="model-step-label">Roadmap</div>', unsafe_allow_html=True)
                for phase in ma["roadmap"]:
                    st.markdown(f"""
                    <div class="model-hyp-item">
                        <strong>{phase['phase']}</strong> ({phase['duration']})
                        <div class="model-hyp-evidence">{phase['focus']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if ma.get("red_flags"):
                st.markdown('<div class="model-step-label flags">Red flags</div>', unsafe_allow_html=True)
                for flag in ma["red_flags"]:
                    st.markdown(f'<div class="model-flag-item">⚠ {flag}</div>', unsafe_allow_html=True)
        except (KeyError, TypeError):
            st.error(ui["json_error"])
            st.session_state.model_answer = None
