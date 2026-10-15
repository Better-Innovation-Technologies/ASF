## Comments and documentation

- Every **public** function, class and module has a docstring/JSDoc describing its contract —
  arguments, return value, raised errors, side effects — not its implementation.
- Inline comments only where the code cannot speak for itself: the *why* of a non-obvious choice.
- Documentation is generated from the docstrings and published with each release.
- No commented-out code; `TODO` only with an issue reference.
