import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from model_answer import build_model_answer_prompt, MODEL_ANSWER_SYSTEM_PROMPT


def test_build_prompt_includes_situation_text():
    prompt = build_model_answer_prompt("Our deployment frequency dropped.")
    assert "Our deployment frequency dropped." in prompt


def test_build_prompt_includes_framework_hint_when_given():
    prompt = build_model_answer_prompt("Some situation", framework_hint="adoption")
    assert '"adoption"' in prompt


def test_build_prompt_omits_framework_hint_when_not_given():
    prompt = build_model_answer_prompt("Some situation")
    assert "method for this one" not in prompt


def test_build_prompt_includes_kb_context_when_given():
    kb_context = [{"id": "x", "title": "Test Entry", "body": "Body text here."}]
    prompt = build_model_answer_prompt("Some situation", kb_context=kb_context)
    assert "Test Entry" in prompt
    assert "Body text here." in prompt


def test_build_prompt_omits_kb_block_when_not_given():
    prompt = build_model_answer_prompt("Some situation")
    assert "Real-world context" not in prompt


def test_system_prompt_defines_both_frameworks():
    assert "diagnostic" in MODEL_ANSWER_SYSTEM_PROMPT
    assert "adoption" in MODEL_ANSWER_SYSTEM_PROMPT
    assert "framework_used" in MODEL_ANSWER_SYSTEM_PROMPT
    assert "Klaeren" in MODEL_ANSWER_SYSTEM_PROMPT or "Klären" in MODEL_ANSWER_SYSTEM_PROMPT
    assert "Ist-Analyse" in MODEL_ANSWER_SYSTEM_PROMPT
