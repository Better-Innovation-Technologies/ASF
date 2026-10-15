## Testing — the testing trophy

Most confidence per minute comes from **integration tests**: when in doubt, write an integration
test first.

| Layer | What |
|---|---|
| **Static** | type checker and linter in CI — the cheapest tests there are |
| **Unit** | pure logic with many cases |
| **Integration** (the widest) | a feature through its real collaborators: real database, real HTTP layer, fake only the external world |
| **End to end** | the few flows that must never break |

- Every acceptance criterion has at least one test; every bug fix has a regression test.
- Test behaviour through public interfaces, not implementation details.
