import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from kb_lookup import load_kb, get_by_id, get_by_ids, match_by_keywords

SAMPLE_KB = [
    {"id": "a", "title": "A", "type": "competency_pattern", "keywords": ["alpha", "structure"], "body": "Body A"},
    {"id": "b", "title": "B", "type": "junior_pitfall", "keywords": ["beta"], "body": "Body B"},
]


def test_load_kb_missing_file_returns_empty(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    assert load_kb(missing) == []


def test_load_kb_malformed_json_returns_empty(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert load_kb(bad) == []


def test_load_kb_valid_file(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(SAMPLE_KB), encoding="utf-8")
    assert load_kb(good) == SAMPLE_KB


def test_load_kb_real_file_in_repo():
    entries = load_kb()
    assert len(entries) == 20


def test_get_by_id_found():
    assert get_by_id("a", SAMPLE_KB)["title"] == "A"


def test_get_by_id_not_found():
    assert get_by_id("z", SAMPLE_KB) is None


def test_get_by_ids_preserves_order_and_skips_missing():
    result = get_by_ids(["b", "z", "a"], SAMPLE_KB)
    assert [e["id"] for e in result] == ["b", "a"]


def test_match_by_keywords_scores_and_limits():
    text = "we need better structure and alpha thinking"
    matches = match_by_keywords(text, SAMPLE_KB, limit=1)
    assert matches == [SAMPLE_KB[0]]


def test_match_by_keywords_no_match_returns_empty():
    assert match_by_keywords("nothing relevant here", SAMPLE_KB) == []


def test_match_by_keywords_filters_by_type():
    matches = match_by_keywords("alpha beta", SAMPLE_KB, entry_types=["junior_pitfall"])
    assert [e["id"] for e in matches] == ["b"]
