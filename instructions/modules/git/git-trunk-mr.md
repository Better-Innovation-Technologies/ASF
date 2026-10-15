## Git workflow — trunk-based with merge requests

```
{{default_branch}}                         ← always releasable
  └── feat/<EpicXXX>-<N>-<short-desc>     ← one short-lived branch per task (hours, at most a day or two)
```

- Small merge requests, merged at least daily; no long-lived feature branches — incomplete work
  hides behind a feature flag.
- **No merge without a green pipeline** (tests, type check, lint, SAST included) and without the
  review/signature the project's gate requires.
- Squash and merge; the merge request title is the commit title.
- Commit messages follow `[agent:<name>] <action> — <reason>` for agents (read by the Commit Gate's
  `asf.linkage`) and a conventional prefix for people (`feat:`, `fix:`, `refactor:`, `docs:`,
  `test:`, `chore:`), always citing the task or bug id.
- Agents never open or merge a merge request on their own unless the method says so.
