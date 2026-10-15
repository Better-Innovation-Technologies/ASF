## Comments and documentation

- **Comments explain why, not what.** The code says what it does; a comment says why it does it
  this way, which alternative was rejected, which constraint forces the shape. A comment that
  repeats the code is deleted.
- A file or module that carries a non-obvious decision opens with a header: what it is for, the
  rule it implements, the requirement or ADR it comes from.
- When the code fixes a bug or implements a requirement, cite its id (`RF-12`, `BUG-031`, `ADR-004`)
  where the reason lives.
- Public functions document their contract: inputs, outputs, errors, and the gotchas a caller needs.
- No commented-out code, no `TODO` without an issue reference.
- Comments are kept true: changing the behaviour and not the comment is a review defect.
