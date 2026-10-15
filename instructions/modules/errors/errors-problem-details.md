## Errors — Problem Details (RFC 9457)

- HTTP APIs return errors as `application/problem+json` with `type`, `title`, `status`, `detail`,
  `instance`, plus extension members when useful (`trace_id`, `errors[]` for validation).
- `type` is a stable URI per kind of problem, documented; clients branch on `type`, never on text.
- **Fail fast**: no empty `catch`, no silent fallback; domain errors are typed classes.
- Never leak stack traces or internal identifiers in `detail`.
