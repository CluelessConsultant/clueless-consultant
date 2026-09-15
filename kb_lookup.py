"""
Loads and matches entries from kb_data.json -- the compiled consulting-kb.
Missing or malformed data always degrades to an empty list, never a crash.
"""
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "kb_data.json"


def load_kb(path: Path = None) -> list:
    path = path or DEFAULT_PATH
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def get_by_id(entry_id: str, kb_entries: list):
    for entry in kb_entries:
        if entry["id"] == entry_id:
            return entry
    return None


def get_by_ids(entry_ids: list, kb_entries: list) -> list:
    by_id = {e["id"]: e for e in kb_entries}
    return [by_id[eid] for eid in entry_ids if eid in by_id]


def match_by_keywords(text: str, kb_entries: list, entry_types: list = None, limit: int = 3) -> list:
    text_lower = text.lower()
    scored = []
    for entry in kb_entries:
        if entry_types and entry["type"] not in entry_types:
            continue
        score = sum(1 for kw in entry.get("keywords", []) if kw.lower() in text_lower)
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda pair: -pair[0])
    return [entry for _, entry in scored[:limit]]
