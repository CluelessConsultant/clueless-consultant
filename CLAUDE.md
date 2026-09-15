# Clueless Consultant Coach — Project Context

**Live:** https://clueless-consultant.streamlit.app/
**Repo:** https://github.com/CluefullConsultant/clueless-consultant

## What it does

Practice loop for junior (AI) consulting skills. Pick one of 8 realistic client scenarios, or paste your own problem statement. Classify the problem, state a hypothesis, ask a diagnostic question, give a recommendation. Claude coaches you using Jazz Rasool's Social Vitamins framework (Challenge, Support, Reflection), grounded in a real knowledge base of junior-consultant competency patterns, pitfalls, and research findings. Then reveal a framework-labeled model answer to compare against your own attempt.

**Absorbed `consulting-problem-structurer` (2026-09-15):** that tool's logic — the structured-brief generation — now lives here as the "reveal model answer" feature (`model_answer.py`). `consulting-problem-structurer` is no longer a live app.

## Key files

- `app.py` — Streamlit UI: scenario/custom-problem toggle, coaching flow, reveal-model-answer step
- `coach.py` — SYSTEM_PROMPT, SCENARIOS, PROBLEM_TYPES, SCENARIO_KB_IDS, SCENARIO_FRAMEWORK
- `model_answer.py` — framework-aware model-answer generation (ported from Structurer)
- `kb_lookup.py` — loads and matches `kb_data.json` (compiled from the separate `consulting-kb` repo)
- `kb_data.json` — compiled KB snapshot; regenerate by running `consulting-kb/build_kb.py` and copying the output here

## The coaching framework

**Jazz Rasool's Social Vitamins** (founder AI Coaching Alliance, author Coaching 5.0):
- CHALLENGE: what is wrong with the user's thinking. Direct. References their actual words. Never softened. Also checks: did they announce their structure explicitly, and was their answer relevant vs. actually resonant.
- SUPPORT: what they genuinely got right. Specific, not generic.
- REFLECTION: one open question. No hint at the answer. Productive discomfort.

**Why challenge first:** Most AI tools only support. Sycophancy leads to atrophy — see the `research-anti-sycophancy-evidence` KB entry for the sourced backing.

## The knowledge base

`consulting-kb` (separate repo) holds 20 curated entries: 2 named case frameworks, 10 competency patterns (derived from ~28 real junior-consultant job postings), 5 junior pitfalls, 3 research findings (from Antony's own thesis research interview with Jazz Rasool). Scenario grounding is static (`SCENARIO_KB_IDS` in `coach.py`); custom-pasted problems are grounded dynamically via keyword matching (`kb_lookup.match_by_keywords`). Missing/malformed `kb_data.json` degrades gracefully — the app never crashes on it.

## Key technical patterns

- Streamlit buttons: never use `st.rerun()` inside button handlers, never combine `value=` and `key=` on the same widget — the `on_click` callback fires before rerender, guaranteeing session state is set when the widget renders.
- JSON parsing: Claude occasionally wraps JSON output in markdown fences or adds preamble — the regex-extraction approach in `app.py` handles this, for both the coaching call and the model-answer call.
- API key: stored in Streamlit Cloud secrets at share.streamlit.io > App settings > Secrets.

## Shared context

For style rules, who Antony is, and the Haik Spitzer meeting context, see `../CLAUDE.md`.
