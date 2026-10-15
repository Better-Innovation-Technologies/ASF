## Git workflow — Git Flow

```
main        ← released versions only, tagged
develop     ← integration
  ├── feature/<desc>    ← from develop, back to develop
  ├── release/<x.y>     ← stabilisation, to main and develop
  └── hotfix/<desc>     ← from main, to main and develop
```

- Use it only when several released versions must be maintained in parallel; otherwise prefer
  trunk-based development.
- No merge without a green pipeline and the review the project's gate requires.
- Commit messages follow `[agent:<name>] <action> — <reason>` for agents and a conventional prefix
  for people, always citing the task or bug id.
