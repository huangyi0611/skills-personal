#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


META_PATTERN = re.compile(
    r"<!-- BOOK_META\s*\n(?P<meta>.*?)\nBOOK_META -->", re.DOTALL
)
REQUIRED_ARRAYS = (
    "concepts",
    "tags",
    "tensions",
    "applications",
    "personal_triggers",
    "transferable_scenarios",
    "open_questions",
    "related_books",
    "connections",
    "review_prompts",
)
CARD_HEADINGS = (
    "## 一句话主旨",
    "## 五个核心概念",
    "## 标签",
    "## 最强反驳",
    "## 可迁移场景",
    "## 与旧书的三处连接",
)
CONNECTION_TYPES = {
    "DIRECT",
    "STRUCTURAL",
    "ANALOGICAL",
    "CONTRADICTORY",
    "COMPLEMENTARY",
    "BOUNDARY",
}
CARD_MAX_CHARS = 1600


def load_metadata(path: Path) -> dict | None:
    match = META_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        return None
    value = json.loads(match.group("meta"))
    return value if isinstance(value, dict) else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deep-reading library records.")
    parser.add_argument("--library-root", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    library_root = (args.library_root or skill_root / "library").resolve()
    books_root = library_root / "books"
    errors: list[str] = []
    checked = 0
    metadata_by_dir: dict[str, dict] = {}

    book_dirs = sorted(path for path in books_root.glob("*") if path.is_dir())
    for book_dir in book_dirs:
        checked += 1
        files = sorted(path for path in book_dir.iterdir() if path.is_file())
        source_files = [path for path in files if path.name.startswith("01-source.")]
        expected = {"02-deep-reading.docx", "03-core-dialogue.md", "04-card.md"}
        unexpected = [
            path.name
            for path in files
            if path.name not in expected and path not in source_files
        ]
        if len(source_files) != 1:
            errors.append(f"{book_dir.name}: expected one 01-source.* file")
        if unexpected:
            errors.append(f"{book_dir.name}: unexpected files: {unexpected}")
        if args.require_complete and len(files) != 4:
            errors.append(f"{book_dir.name}: completed record must contain exactly 4 files")

        analysis = book_dir / "02-deep-reading.docx"
        if args.require_complete and (not analysis.is_file() or analysis.stat().st_size == 0):
            errors.append(f"{book_dir.name}: missing or empty 02-deep-reading.docx")

        dialogue = book_dir / "03-core-dialogue.md"
        if not dialogue.is_file():
            errors.append(f"{book_dir.name}: missing 03-core-dialogue.md")
            continue
        try:
            meta = load_metadata(dialogue)
        except json.JSONDecodeError as error:
            errors.append(f"{book_dir.name}: invalid BOOK_META JSON: {error}")
            continue
        if meta is None:
            errors.append(f"{book_dir.name}: missing or invalid BOOK_META block")
            continue
        metadata_by_dir[book_dir.name] = meta
        for key in ("title", "author", "thesis", "strongest_counterargument"):
            if args.require_complete and not str(meta.get(key, "")).strip():
                errors.append(f"{book_dir.name}: missing metadata field {key}")
        for key in REQUIRED_ARRAYS:
            if not isinstance(meta.get(key), list):
                errors.append(f"{book_dir.name}: metadata field {key} must be an array")
        if args.require_complete and len(meta.get("concepts", [])) != 5:
            errors.append(f"{book_dir.name}: concepts must contain exactly 5 items")
        if args.require_complete and not (2 <= len(meta.get("tags", [])) <= 12):
            errors.append(f"{book_dir.name}: tags must contain 2-12 items")
        if args.require_complete and not meta.get("transferable_scenarios", []):
            errors.append(f"{book_dir.name}: transferable_scenarios cannot be empty")

        status = str(meta.get("connection_status", ""))
        connections = meta.get("connections", [])
        if args.require_complete:
            if status == "first_book" and connections:
                errors.append(f"{book_dir.name}: first_book must not contain connections")
            elif status == "complete" and len(connections) != 3:
                errors.append(f"{book_dir.name}: complete connection pass requires 3 items")
            elif status == "insufficient_meaningful_connections":
                if len(connections) >= 3 or not str(meta.get("connection_gap", "")).strip():
                    errors.append(
                        f"{book_dir.name}: insufficient connections require fewer than 3 items and a gap explanation"
                    )
            elif status not in {"first_book", "complete", "insufficient_meaningful_connections"}:
                errors.append(f"{book_dir.name}: invalid final connection_status {status!r}")
        for index, connection in enumerate(connections, 1):
            if not isinstance(connection, dict):
                errors.append(f"{book_dir.name}: connection {index} must be an object")
                continue
            for key in ("book_dir", "book_title", "type", "concept", "note"):
                if not str(connection.get(key, "")).strip():
                    errors.append(f"{book_dir.name}: connection {index} missing {key}")
            if connection.get("type") not in CONNECTION_TYPES:
                errors.append(f"{book_dir.name}: connection {index} has invalid type")
            if connection.get("book_dir") == book_dir.name:
                errors.append(f"{book_dir.name}: connection {index} points to itself")

        card = book_dir / "04-card.md"
        if not card.is_file():
            errors.append(f"{book_dir.name}: missing 04-card.md")
        elif args.require_complete:
            card_text = card.read_text(encoding="utf-8")
            if "待完成" in card_text:
                errors.append(f"{book_dir.name}: card still contains placeholders")
            if len(card_text) > CARD_MAX_CHARS:
                errors.append(
                    f"{book_dir.name}: card exceeds {CARD_MAX_CHARS} characters ({len(card_text)})"
                )
            for heading in CARD_HEADINGS:
                if heading not in card_text:
                    errors.append(f"{book_dir.name}: card missing heading {heading}")
            concept_lines = re.findall(r"(?m)^\s*[1-5]\.\s+.+$", card_text)
            if len(concept_lines) != 5:
                errors.append(f"{book_dir.name}: card must show exactly five numbered concepts")

    for book_dir, meta in metadata_by_dir.items():
        for index, connection in enumerate(meta.get("connections", []), 1):
            target = str(connection.get("book_dir", ""))
            if target and target not in metadata_by_dir:
                errors.append(f"{book_dir}: connection {index} target does not exist: {target}")

    catalog_path = library_root / "catalog.json"
    concepts_path = library_root / "concepts.md"
    if not catalog_path.is_file():
        errors.append("library/catalog.json is missing")
    else:
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            if args.require_complete:
                for entry in catalog.get("books", []):
                    if entry.get("book_dir") in metadata_by_dir and entry.get("status") != "complete":
                        errors.append(f"{entry.get('book_dir')}: catalog status is not complete; rebuild indexes")
        except json.JSONDecodeError as error:
            errors.append(f"library/catalog.json is invalid JSON: {error}")
    if not concepts_path.is_file():
        errors.append("library/concepts.md is missing")
    elif args.require_complete:
        concepts_text = concepts_path.read_text(encoding="utf-8")
        for book_dir, meta in metadata_by_dir.items():
            for concept in meta.get("concepts", []):
                if str(concept).strip() and str(concept).strip() not in concepts_text:
                    errors.append(f"{book_dir}: concept missing from concepts.md: {concept}")

    result = {
        "status": "ok" if not errors else "error",
        "checked_books": checked,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
