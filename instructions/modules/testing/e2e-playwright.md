## Testing — end to end with Playwright

- Main user flows are covered by **Playwright** tests, written from the acceptance criteria in BDD
  form (Given / When / Then).
- Locate elements by role and accessible name, never by CSS structure.
- Each test creates its own data and cleans up; no dependency on test order.
- Traces and screenshots are kept for failed runs in CI.
