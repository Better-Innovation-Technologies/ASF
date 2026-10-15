## Language

| What | Language |
|---|---|
| Technical identifiers (framework concepts: `router`, `handler`, `repository`, `Props`) | **English** |
| **Domain identifiers** (business entities, rules, states, events) | **{{business_language}}**, untranslated |
| Comments, docstrings, commit messages, merge requests, documentation | **{{prose_language}}** |
| Log and error messages for operators | **{{prose_language}}** |

This is the *ubiquitous language* taken literally: the words the business uses are the words the
code uses. Translating a domain term to English creates a second vocabulary that only developers
speak, and every conversation with the business then needs a translation where misunderstandings
live. The technical scaffolding around the domain stays English, because that is the vocabulary of
the frameworks.

### Rules

- Every domain term is recorded in `{{glossary_path}}` with its definition and the identifier form
  used in code (casing per language: `PascalCase` types, `camelCase`/`snake_case` members).
- Identifiers use the business word **without accents or non-ASCII characters** (transliterate:
  `qualità` → `qualita`), so that every tool, file system and URL handles them.
- One business concept, one word. When the business uses two words for one thing, the glossary
  chooses one and says so.
- A new domain term enters the glossary in the same merge request that first uses it.

User-facing text follows the localization rules of this file, never a string literal in the source.
