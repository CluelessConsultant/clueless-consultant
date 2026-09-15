"""
Clueless Consultant - AI Coaching Tool for Junior Consultants
Built with Claude. Architecture: Jazz Rasool's Social Vitamins (Support, Challenge, Reflection)
Run with: python -m streamlit run app.py
"""

import streamlit as st
import anthropic
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
        "model_answer_heading": "Model answer",
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
        "model_answer_heading": "Musterlösung",
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

    /* Section labels (e.g. model answer heading) */
    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.75rem;
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
if "language" not in st.session_state:
    st.session_state.language = "en"
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "scenario"
if "model_answer" not in st.session_state:
    st.session_state.model_answer = None

kb_entries = load_kb()

# ── Language toggle ──────────────────────────────────────────
st.radio(
    "Language",
    options=["en", "de"],
    format_func=lambda code: "English" if code == "en" else "Deutsch",
    horizontal=True,
    key="language",
    label_visibility="collapsed",
)
lang = st.session_state.language
ui = UI_TEXT[lang]

# ── Hero ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-tag">{ui['hero_tag']}</div>
    <div class="hero-title">{ui['hero_title']}</div>
    <div class="hero-subtitle">
        {ui['hero_subtitle']}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input mode toggle ────────────────────────────────────────
st.markdown(f'<div class="input-label">{ui["mode_label"]}</div>', unsafe_allow_html=True)
st.radio(
    "input_mode",
    options=["scenario", "custom"],
    format_func=lambda m: ui["mode_scenario"] if m == "scenario" else ui["mode_custom"],
    horizontal=True,
    key="input_mode",
    label_visibility="collapsed",
)

# ── Scenario or custom problem ───────────────────────────────
scenario = None
custom_problem = ""

if st.session_state.input_mode == "scenario":
    scenario = SCENARIOS[st.session_state.scenario_index]
    st.markdown(f"""
    <div class="scenario-card">
        <div class="scenario-label">{ui['scenario_label']} &nbsp;|&nbsp; {scenario['context'][lang]}</div>
        <div class="scenario-text">{scenario['text'][lang]}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f'<div class="input-label">{ui["custom_label"]}</div>', unsafe_allow_html=True)
    custom_problem = st.text_area(
        "custom_problem",
        placeholder=ui["custom_placeholder"],
        height=110,
        label_visibility="collapsed",
        key="custom_problem",
    )

# ── Inputs ────────────────────────────────────────────────────
st.markdown(f'<div class="input-label">{ui["classification_label"]}</div>', unsafe_allow_html=True)
classification = st.selectbox(
    "classification",
    PROBLEM_TYPES,
    format_func=lambda key: PROBLEM_TYPE_LABELS[lang][key],
    label_visibility="collapsed"
)

st.markdown(f'<div class="input-label">{ui["hypothesis_label"]}</div>', unsafe_allow_html=True)
hypothesis = st.text_area(
    "hypothesis",
    placeholder=ui["hypothesis_placeholder"],
    height=90,
    label_visibility="collapsed"
)

st.markdown(f'<div class="input-label">{ui["question_label"]}</div>', unsafe_allow_html=True)
first_question = st.text_area(
    "first_question",
    placeholder=ui["question_placeholder"],
    height=75,
    label_visibility="collapsed"
)

st.markdown(f'<div class="input-label">{ui["recommendation_label"]}</div>', unsafe_allow_html=True)
recommendation = st.text_area(
    "recommendation",
    placeholder=ui["recommendation_placeholder"],
    height=75,
    label_visibility="collapsed"
)

# ── Buttons ───────────────────────────────────────────────────
col_submit, col_next, _ = st.columns([1.2, 1.2, 2])

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
    st.session_state.result = None
    st.session_state.final_message = None
    st.session_state.model_answer = None

if st.session_state.input_mode == "scenario":
    col_next.button(ui["next_button"], on_click=next_scenario)

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
                    f'<div style="font-family:monospace;font-size:0.75rem;color:#6b7280;'
                    f'background:#f9fafb;padding:1rem 1.25rem;border-radius:8px;'
                    f'border:1px solid #e5e7eb;white-space:pre-wrap;line-height:1.6;">'
                    f'Evaluating your response...\n{raw}&#9646;</div>',
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

    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

    ratio = data.get("vitamin_ratio", "balanced")
    ratio_class_map = {
        "heavy_challenge":  "ratio-heavy-challenge",
        "balanced":         "ratio-balanced",
        "heavy_reflection": "ratio-heavy-reflection"
    }
    ratio_class = ratio_class_map.get(ratio, "ratio-balanced")
    ratio_label = ui["ratio_labels"].get(ratio, ui["ratio_labels"]["balanced"])

    st.markdown(
        f'<span class="ratio-badge {ratio_class}">{ratio_label}</span>'
        f'<span style="font-size:0.7rem;color:#9ca3af;margin-left:0.75rem;">'
        f'{ui["framework_note"]}'
        f'</span>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="vitamin-challenge">
        <div class="vitamin-challenge-label">{ui['challenge_label']}</div>
        <div class="vitamin-challenge-text">{data['challenge']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vitamin-support">
        <div class="vitamin-support-label">{ui['support_label']}</div>
        <div class="vitamin-support-text">{data['support']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vitamin-reflection">
        <div class="vitamin-reflection-label">{ui['reflection_label']}</div>
        <div class="vitamin-reflection-text">{data['reflection_question']}</div>
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
    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
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
        st.markdown(f'<div class="section-label">{ui["model_answer_heading"]}</div>', unsafe_allow_html=True)

        if ma["framework_used"] == "diagnostic":
            st.markdown(f"**Klären:** {ma['klaeren']['restated_problem']}")
            for assumption in ma["klaeren"]["clarifying_assumptions"]:
                st.markdown(f"- {assumption}")

            st.markdown(f"**Strukturieren:** {ma['strukturieren']['root_problem']}")
            for branch in ma["strukturieren"]["branches"]:
                st.markdown(f"- {branch['area']}")
                for sub in branch["sub_issues"]:
                    st.markdown(f"  - {sub}")

            st.markdown("**Hypothese:**")
            for h in ma["hypothese"]:
                st.markdown(f"- {h['hypothesis']} _(evidence: {h['evidence']})_")

            st.markdown("**Analysieren:**")
            for q in ma["analysieren"]["diagnostic_questions"]:
                st.markdown(f"- {q['question']} _(reveals: {q['what_it_reveals']})_")

            st.markdown(f"**Synthetisieren:** {ma['synthetisieren']['recommendation']}")
            ws = ma["synthetisieren"]["first_workshop"]
            st.markdown(f"First workshop: {ws['format']} ({ws['duration']}) — {ws['key_output']}")
        else:
            ist = ma["ist_analyse"]
            st.markdown("**Ist-Analyse:**")
            for dim, val in ist.items():
                st.markdown(f"- {dim}: {val}")

            st.markdown(f"**Zielbild:** {ma['zielbild']}")

            st.markdown("**Gap-Analyse:**")
            for gap in ma["gap_analyse"]:
                st.markdown(f"- {gap}")

            st.markdown("**Operationalisieren:**")
            for ws in ma["operationalisieren"]:
                st.markdown(f"- {ws['workstream']}: {ws['description']}")

            st.markdown("**Roadmap:**")
            for phase in ma["roadmap"]:
                st.markdown(f"- {phase['phase']} ({phase['duration']}): {phase['focus']}")

        if ma.get("red_flags"):
            st.markdown("**Red flags:**")
            for flag in ma["red_flags"]:
                st.markdown(f"- ⚠ {flag}")
