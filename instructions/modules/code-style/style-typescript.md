## Code style — TypeScript

- `strict` on, plus `noUncheckedIndexedAccess`; `tsc --noEmit` and ESLint (typescript-eslint
  recommended-type-checked) block CI.
- Formatting by the project formatter (Prettier or the ESLint stylistic rules) — never by hand.
- No `any` without a comment explaining it; prefer `unknown` and narrow.
- `PascalCase` types and components, `camelCase` functions and variables, `UPPER_SNAKE_CASE`
  constants; files named after their main export.
- Prefer union types and `as const` objects to enums for closed sets of strings.
- Every promise is awaited or explicitly handled (`no-floating-promises`).
