#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


META_PATTERN = re.compile(
    r"<!-- BOOK_META\s*\n(?P<meta>.*?)\nBOOK_META -->", re.DOTALL
)


def load_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = META_PATTERN.search(text)
    if not match:
        raise ValueError(f"Missing BOOK_META block: {path}")
    value = json.loads(match.group("meta"))
    if not isinstance(value, dict):
        raise ValueError(f"BOOK_META must be a JSON object: {path}")
    return value


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def clean_inline(value: object) -> str:
    return " ".join(str(value).replace("|", "∣").split())


def link_for(entry: dict) -> str:
    title = clean_inline(entry.get("title", entry["book_dir"]))
    return f"[《{title}》](books/{entry['book_dir']}/04-card.md)"


def build_concepts_markdown(entries: list[dict], generated_at: str) -> str:
    complete = [entry for entry in entries if entry["status"] == "complete"]
    concept_map: dict[str, list[dict]] = defaultdict(list)
    tag_map: dict[str, list[dict]] = defaultdict(list)
    by_dir = {entry["book_dir"]: entry for entry in complete}

    for entry in complete:
        for concept in entry.get("concepts", []):
            concept = clean_inline(concept)
            if concept:
                concept_map[concept].append(entry)
        for tag in entry.get("tags", []):
            tag = clean_inline(tag)
            if tag:
                tag_map[tag].append(entry)

    lines = [
        "# 跨书概念索引",
        "",
        "> 这是渐进式检索入口。先定位概念，再读取候选书的 04-card.md。",
        f"> 更新时间：{generated_at}",
        "",
        "## 概念到书",
        "",
    ]
    if not concept_map:
        lines.extend(["暂无已完成书目。", ""])
    else:
        for concept in sorted(concept_map, key=str.casefold):
            lines.extend([f"### {concept}", ""])
            for entry in sorted(concept_map[concept], key=lambda item: item["book_dir"]):
                thesis = clean_inline(entry.get("thesis", ""))
                lines.append(f"- {link_for(entry)} — {thesis}")
            lines.append("")

    lines.extend(["## 标签到书", ""])
    if not tag_map:
        lines.extend(["暂无标签。", ""])
    else:
        for tag in sorted(tag_map, key=str.casefold):
            books = "、".join(link_for(entry) for entry in sorted(tag_map[tag], key=lambda item: item["book_dir"]))
            lines.append(f"- **{tag}**：{books}")
        lines.append("")

    lines.extend(["## 跨书连接", ""])
    connection_count = 0
    for entry in sorted(complete, key=lambda item: item["book_dir"]):
        for connection in entry.get("connections", []):
            target = by_dir.get(str(connection.get("book_dir", "")))
            if not target:
                continue
            connection_count += 1
            kind = clean_inline(connection.get("type", ""))
            concept = clean_inline(connection.get("concept", ""))
            note = clean_inline(connection.get("note", ""))
            lines.append(
                f"- {link_for(entry)} ↔ {link_for(target)} — **{kind}** / {concept}：{note}"
            )
    if connection_count == 0:
        lines.append("暂无跨书连接。")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild catalog and concepts index.")
    parser.add_argument("--library-root", type=Path)
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    library_root = (args.library_root or skill_root / "library").resolve()
    books_root = library_root / "books"
    books_root.mkdir(parents=True, exist_ok=True)
    entries = []

    for book_dir in sorted(path for path in books_root.glob("*") if path.is_dir()):
        dialogue_path = book_dir / "03-core-dialogue.md"
        if not dialogue_path.is_file():
            continue
        meta = load_metadata(dialogue_path)
        source_files = sorted(book_dir.glob("01-source.*"))
        analysis_path = book_dir / "02-deep-reading.docx"
        card_path = book_dir / "04-card.md"
        meta["book_dir"] = book_dir.name
        meta["files"] = {
            "source": source_files[0].name if len(source_files) == 1 else "",
            "analysis": analysis_path.name if analysis_path.is_file() else "",
            "dialogue": dialogue_path.name,
            "card": card_path.name if card_path.is_file() else "",
        }
        meta["status"] = (
            "complete"
            if len(source_files) == 1 and analysis_path.is_file() and card_path.is_file()
            and meta.get("connection_status") != "pending"
            else "in_progress"
        )
        entries.append(meta)

    generated_at = datetime.now(timezone.utc).isoformat()
    catalog = {
        "schema_version": 2,
        "generated_at": generated_at,
        "book_count": len(entries),
        "complete_book_count": sum(entry["status"] == "complete" for entry in entries),
        "books": entries,
    }
    catalog_path = library_root / "catalog.json"
    concepts_path = library_root / "concepts.md"
    atomic_write(catalog_path, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    atomic_write(concepts_path, build_concepts_markdown(entries, generated_at))
    print(
        json.dumps(
            {
                "catalog": str(catalog_path),
                "concepts": str(concepts_path),
                "book_count": len(entries),
                "complete_book_count": catalog["complete_book_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
