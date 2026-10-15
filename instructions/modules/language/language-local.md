## Language

The whole repository is written in **{{prose_language}}**: identifiers, comments, commit messages,
merge requests, documentation, log messages. Only the vocabulary imposed by frameworks and
libraries stays as it is (`useEffect`, `router`, `SELECT`).

Choose this only for a team and a business that will stay in one language: external contributors,
vendors and most review tooling read English, and switching later means renaming everything.

### Rules

- Identifiers use **ASCII only** — transliterate accents (`qualità` → `qualita`), so that every
  tool, file system and URL handles them.
- Domain terms come from `{{glossary_path}}`: one business concept, one word, defined once.
- Do not mix languages inside one identifier (`getFattura` is wrong: `leggiFattura`).
- User-facing text follows the localization rules of this file, never a string literal in the source.
