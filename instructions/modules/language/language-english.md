## Language

Everything written in the repository is in **English**: identifiers, comments, docstrings,
commit messages, merge request titles and descriptions, technical documentation, log messages.
English is the lingua franca of the tooling, of the libraries and of most reviewers; mixing
languages inside one codebase forces every reader to translate twice.

### Domain terms — one glossary

The business speaks **{{business_language}}**. Every domain term gets **one** English name, decided
once and recorded in `{{glossary_path}}` (term in {{business_language}} → English name → one-line
definition). Code, tests, API fields and database columns use that English name and nothing else:
two English words for one business concept is a bug in the language, not a matter of style.

- A new domain term enters the glossary **in the same merge request** that first uses it.
- Do not translate on the fly in code review: if the glossary has no entry, add it first.
- Names follow the business meaning, not the technical one (`placeOrder`, not `insertRecord`).

### What stays in another language

User-facing text is not code: it follows the localization rules of this file, never a string
literal in the source.
