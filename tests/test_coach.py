import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from coach import build_system_prompt, SCENARIOS, SCENARIO_KB_IDS, SCENARIO_FRAMEWORK
from kb_lookup import load_kb


def test_build_system_prompt_without_kb_context_omits_context_block():
    prompt = build_system_prompt("en")
    assert "REAL-WORLD CONTEXT" not in prompt


def test_build_system_prompt_with_kb_context_includes_it():
    kb_context = [{"id": "x", "title": "Test Entry", "body": "Test body content."}]
    prompt = build_system_prompt("en", kb_context=kb_context)
    assert "REAL-WORLD CONTEXT" in prompt
    assert "Test Entry" in prompt
    assert "Test body content." in prompt


def test_build_system_prompt_empty_kb_context_omits_block():
    prompt = build_system_prompt("en", kb_context=[])
    assert "REAL-WORLD CONTEXT" not in prompt


def test_every_scenario_has_kb_ids_and_framework():
    scenario_ids = {s["id"] for s in SCENARIOS}
    assert scenario_ids == set(SCENARIO_KB_IDS.keys())
    assert scenario_ids == set(SCENARIO_FRAMEWORK.keys())


def test_scenario_framework_values_are_valid():
    assert set(SCENARIO_FRAMEWORK.values()) <= {"framework-diagnostic", "framework-adoption"}


def test_new_coaching_lenses_present_in_base_prompt():
    prompt = build_system_prompt("en")
    assert "resonance" in prompt.lower()
    assert "structure" in prompt.lower()


def test_all_scenario_kb_ids_resolve_in_kb_data():
    kb_entries = load_kb()
    real_ids = {entry["id"] for entry in kb_entries}
    referenced_ids = {eid for ids in SCENARIO_KB_IDS.values() for eid in ids}
    missing = referenced_ids - real_ids
    assert not missing, f"SCENARIO_KB_IDS references unknown KB ids: {missing}"
