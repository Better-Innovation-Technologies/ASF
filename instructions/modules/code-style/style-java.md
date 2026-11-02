## Code style — Java

- Formatting with **google-java-format** applied through Spotless (`spotlessCheck`); linting with
  **Checkstyle**. Both block CI, with a ratchet for existing debt — never format by hand.
- No wildcard imports, no unused imports; static imports only for test assertions and constants.
- `PascalCase` classes and records, `camelCase` methods and variables, `UPPER_SNAKE_CASE`
  constants, lower-case package names without underscores.
- Nullability is explicit: packages are `@NullMarked` (JSpecify) and a value that may be absent is
  `@Nullable`; `Optional` only as a return type, never as a field or a parameter.
- Prefer immutable `record`s and `final` fields; `enum` or a `sealed` hierarchy for closed sets.
- No raw types and no unchecked casts without a comment explaining why.
- No empty `catch` and no `catch (Exception e)` that only logs; catch what you can handle, rethrow
  the rest with its cause.
