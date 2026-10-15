## Testing — the test pyramid

| Kind | Scope | Notes |
|---|---|---|
| **Unit** | services, domain logic, utilities | no real database or network; fast |
| **Integration** | API endpoints, database queries, adapters | a **real** database — do not mock the database |
| **Frontend** | components with logic, hooks | React Testing Library — behaviour, not internals |
| **End to end** | the main user flows | few, stable, run on every merge |

- Every acceptance criterion of a task has at least one test, written in the same session as the
  implementation.
- Every bug fix comes with a regression test that fails before the fix.
- Tests are isolated and order-independent; no shared mutable fixtures.
