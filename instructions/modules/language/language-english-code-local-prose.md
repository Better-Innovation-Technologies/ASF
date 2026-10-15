## Language

| What | Language |
|---|---|
| Identifiers (variables, functions, classes, files, API fields, DB columns) | **English** |
| Comments and docstrings | **{{prose_language}}** |
| Commit messages, merge request titles and descriptions | **{{prose_language}}** |
| Technical documentation (`docs/`, READMEs, ADRs) | **{{prose_language}}** |
| Log messages and error messages for operators | **{{prose_language}}** |

Identifiers stay in English because they meet libraries, frameworks and generated code that are
English; the prose is in the team's language because that is where precision matters most — a
comment that explains *why* is worth less when its author writes it in a second language.

### Domain terms — one glossary

The business speaks **{{business_language}}**. Every domain term has **one** English identifier,
recorded in `{{glossary_path}}` (term in {{business_language}} → English identifier → definition).
Comments and documentation use the business term; code uses the identifier from the glossary.

- A new domain term enters the glossary in the same merge request that first uses it.
- Never two identifiers for one business concept, never one identifier for two.
- Names follow the business meaning, not the technical one.

User-facing text follows the localization rules of this file, never a string literal in the source.
