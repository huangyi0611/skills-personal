# Retrieval card and connection pass

## Purpose

Use `04-card.md` as the low-cost retrieval layer. It must be understandable
without opening the DOCX, yet small enough to scan alongside several other
books. Target no more than 1,600 visible characters or roughly 400 English
words. Do not include long quotations or chapter summaries.

## Card schema

```markdown
# 《书名》阅读卡

## 一句话主旨

用一个可争论、可迁移的句子表达全书核心命题。

## 五个核心概念

1. **概念一** — 一句解释
2. **概念二** — 一句解释
3. **概念三** — 一句解释
4. **概念四** — 一句解释
5. **概念五** — 一句解释

## 标签

`标签一` `标签二` `标签三`

## 最强反驳

对中心命题最有力、最公平的反驳，而不是稻草人。

## 可迁移场景

- 场景一
- 场景二

## 与旧书的三处连接

- **STRUCTURAL**｜《旧书》｜共同概念｜结构如何相同、差异在哪里
- **CONTRADICTORY**｜《旧书》｜冲突概念｜两本书为何给出不同解释
- **BOUNDARY**｜《旧书》｜边界概念｜一本书如何限定另一本书
```

The visible card and the `BOOK_META` block in `03-core-dialogue.md` must agree.
For the first book, write `暂无旧书可连接`. When fewer than three defensible
connections exist, list the real connections and state the gap plainly.

## Mandatory connection pass

Perform this after the book analysis and reader dialogue are mature:

1. Read `library/concepts.md` only.
2. Select up to five candidate concepts based on mechanism, tension, problem,
   decision, boundary, or open question—not title similarity.
3. Open only the candidate books' `04-card.md` files.
4. If the card is insufficient, open the relevant part of
   `03-core-dialogue.md`; open the DOCX only when deeper evidence is required.
5. Rank candidate links by explanatory value and retain the strongest three.
6. Classify each retained link as `DIRECT`, `STRUCTURAL`, `ANALOGICAL`,
   `CONTRADICTORY`, `COMPLEMENTARY`, or `BOUNDARY`.
7. State both the connection and the important difference. Never write “both
   books discuss X” as a complete connection.
8. Update the dialogue metadata and visible card, then run
   `scripts/rebuild_catalog.py` to regenerate `concepts.md`.

## Meaningfulness test

Keep a connection only if it does at least one of the following:

- explains the current book more accurately;
- reveals a genuine contradiction in assumptions or recommendations;
- supplies a missing mechanism or level of analysis;
- marks where an analogy breaks;
- changes a prediction, decision, or action;
- shows that the reader's own view evolved across books.

Prefer fewer honest connections plus an explicit gap over three decorative
associations.
