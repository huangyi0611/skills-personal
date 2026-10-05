#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date
from pathlib import Path


def safe_segment(value: str, fallback: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-. ")
    return (value or fallback)[:80]


def metadata(title: str, author: str, language: str) -> dict:
    return {
        "schema_version": 2,
        "title": title,
        "author": author,
        "completed_on": "",
        "source_language": language,
        "thesis": "",
        "concepts": [],
        "tags": [],
        "tensions": [],
        "applications": [],
        "personal_triggers": [],
        "strongest_counterargument": "",
        "transferable_scenarios": [],
        "open_questions": [],
        "related_books": [],
        "connection_status": "pending",
        "connection_gap": "",
        "connections": [],
        "review_prompts": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a four-file book record.")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="未知作者")
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--library-root", type=Path)
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Source file not found: {source}")

    skill_root = Path(__file__).resolve().parents[1]
    library_root = (args.library_root or skill_root / "library").resolve()
    books_root = library_root / "books"
    books_root.mkdir(parents=True, exist_ok=True)

    directory_name = (
        f"{safe_segment(args.author, 'unknown-author')}__"
        f"{safe_segment(args.title, 'untitled')}"
    )
    book_dir = books_root / directory_name
    if book_dir.exists():
        raise SystemExit(
            f"Book directory already exists; resume it instead of overwriting: {book_dir}"
        )
    book_dir.mkdir()

    source_target = book_dir / f"01-source{source.suffix.lower()}"
    shutil.copy2(source, source_target)

    meta = json.dumps(
        metadata(args.title.strip(), args.author.strip(), args.language.strip()),
        ensure_ascii=False,
        indent=2,
    )
    dialogue = (
        f"<!-- BOOK_META\n{meta}\nBOOK_META -->\n\n"
        f"# {args.title.strip()} 这次阅读留下了什么\n\n"
        "> 状态：阅读与对话进行中。完成后删除本行。\n\n"
        "## 对话轨迹\n\n"
        "## 我的核心判断\n\n"
        "## 我原来怎么想 现在怎么想\n\n"
        "## 我与作者的分歧\n\n"
        "## 对我的作用\n\n"
        "## 决定与行动实验\n\n"
        "## 仍然悬而未决\n\n"
        "## 与旧书的三处连接\n\n"
        "## 1 7 30 90 天记忆检索\n"
    )
    dialogue_path = book_dir / "03-core-dialogue.md"
    dialogue_path.write_text(dialogue, encoding="utf-8")

    card = (
        f"# 《{args.title.strip()}》阅读卡\n\n"
        "> 状态：待完成\n\n"
        "## 一句话主旨\n\n待完成\n\n"
        "## 五个核心概念\n\n"
        "1. 待完成\n2. 待完成\n3. 待完成\n4. 待完成\n5. 待完成\n\n"
        "## 标签\n\n`待完成`\n\n"
        "## 最强反驳\n\n待完成\n\n"
        "## 可迁移场景\n\n- 待完成\n\n"
        "## 与旧书的三处连接\n\n- 待完成\n"
    )
    card_path = book_dir / "04-card.md"
    card_path.write_text(card, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "initialized",
                "book_dir": str(book_dir),
                "source": str(source_target),
                "analysis": str(book_dir / "02-deep-reading.docx"),
                "dialogue": str(dialogue_path),
                "card": str(card_path),
                "initialized_on": date.today().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
