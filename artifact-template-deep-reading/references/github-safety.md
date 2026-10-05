# GitHub and source safety

The reader may own a copy of an ebook without holding the right to redistribute
it. Before publishing a repository:

- Use a private repository for copyrighted ebooks unless the work is public
  domain, openly licensed, or the reader has redistribution permission.
- For a public repository, commit only reusable skill instructions, references,
  and scripts unless the reader explicitly approves additional files. Keep the
  catalog, concept index, ebooks, analysis, dialogue, cards, and annotations in
  a separate private library.
- Remove account names, download tokens, annotations, purchase receipts, and
  other personal metadata from files intended for public release.
- Consider Git LFS for large PDF, EPUB, MOBI, AZW3, and DOCX files. Verify that
  collaborators can retrieve LFS objects before relying on it.
- Do not upload a book, push a repository, change visibility, or rewrite Git
  history without an explicit user request.
- Before every public push, inspect the exact staged file list and search it for
  ebook/document extensions, personal paths, account names, tokens, book titles,
  and dialogue fragments. Stop the push if any unapproved item appears.

The generated analysis should quote sparingly and transformatively. Prefer
paraphrase with precise locations over long passages from the source.
