# Repository contract

## Layout

```text
artifact-template-deep-reading/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── library/
    ├── catalog.json
    ├── concepts.md
    └── books/
        └── <author>__<title>/
            ├── 01-source.<ext>
            ├── 02-deep-reading.docx
            ├── 03-core-dialogue.md
            └── 04-card.md
```

Each completed book directory must contain exactly these four files. Keep OCR,
chapter extracts, screenshots, draft data, renders, and temporary notes in the
task workspace, never beside the book.

## Core dialogue metadata

Start `03-core-dialogue.md` with a valid JSON metadata block. Keep the markers
on their own lines so the deterministic index scripts can parse them.

```markdown
<!-- BOOK_META
{
  "schema_version": 2,
  "title": "书名",
  "author": "作者",
  "completed_on": "YYYY-MM-DD",
  "source_language": "zh-CN",
  "thesis": "一句话写出全书的核心主张",
  "concepts": ["概念一", "概念二", "概念三", "概念四", "概念五"],
  "tags": ["领域", "问题", "机制"],
  "tensions": ["价值或解释之间的张力"],
  "applications": ["适用的决策或生活情境"],
  "personal_triggers": ["以后遇到什么情境时应想起本书"],
  "strongest_counterargument": "对核心命题最有力的反驳",
  "transferable_scenarios": ["可以迁移的现实场景"],
  "open_questions": ["仍未解决的问题"],
  "related_books": ["作者__书名"],
  "connection_status": "pending",
  "connection_gap": "",
  "connections": [],
  "review_prompts": ["不翻书能否复述的检索问题"]
}
BOOK_META -->
```

Use exactly five core concepts and 2–12 tags. Use 1–6 tensions, 1–8
applications, 1–8 personal triggers, 1–8 transferable scenarios, 0–8 open
questions, and 3–7 review prompts.

Represent each connection as:

```json
{
  "book_dir": "旧书作者__旧书名",
  "book_title": "旧书名",
  "type": "STRUCTURAL",
  "concept": "共同或冲突的概念",
  "note": "它如何呼应、矛盾、补足或限定当前这本书"
}
```

Allowed types are `DIRECT`, `STRUCTURAL`, `ANALOGICAL`, `CONTRADICTORY`,
`COMPLEMENTARY`, and `BOUNDARY`. Never treat analogy as equivalence.

Set `connection_status` to:

- `first_book` when no older completed book exists; keep `connections` empty;
- `complete` when three meaningful connections are recorded;
- `insufficient_meaningful_connections` only when fewer than three defensible
  links exist; explain the shortfall in `connection_gap`.

## Core dialogue body

Use these sections:

1. `# 这次阅读留下了什么`
2. `## 对话轨迹` — questions, why they mattered, and concise answers
3. `## 我的核心判断` — first-person only when grounded in the reader's words
4. `## 我原来怎么想 现在怎么想`
5. `## 我与作者的分歧`
6. `## 对我的作用`
7. `## 决定与行动实验`
8. `## 仍然悬而未决`
9. `## 与旧书的三处连接`
10. `## 1 7 30 90 天记忆检索`

This file is not a transcript. Remove greetings, repetition, and dead ends
unless they reveal a meaningful change of mind. Label paraphrases. Quote the
reader only when the words were actually said.

## Session states

- `initialized`: source, dialogue skeleton, and card skeleton exist.
- `dialogue`: first-pass essence delivered; reflective questions in progress.
- `finalizing`: dialogue and DOCX complete; card and connections in progress.
- `complete`: exactly four files exist, metadata parses, DOCX is visually
  verified, card is concise, indexes are rebuilt, and validation passes.

Never label an incomplete record as complete.

## Public skill repository boundary

The reusable skill may live in a public repository. Treat `library/` as private
runtime data by default. Use `--library-root` to place personal book records in
a separate private directory or private repository. Do not stage ebooks,
finished DOCX files, dialogue records, retrieval cards, generated indexes, or
personal annotations in the public skill repository unless the reader gives
explicit file-level permission.
