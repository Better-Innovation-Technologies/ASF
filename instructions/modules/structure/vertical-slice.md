## Internal structure — vertical slices (by feature)

Code is organised **by feature, not by technical layer**: each slice contains everything one use
case needs — request, handler, validation, data access, response, tests.

```
features/
└── <feature>/<use-case>/
    ├── handler        # the whole use case, top to bottom
    ├── schema         # request/response
    └── test
```

- Maximise cohesion inside a slice, minimise coupling between slices: a slice never calls another
  slice's handler; shared domain logic is extracted only when two slices really share a rule.
- Each slice may choose its own internal technique — a transaction script for simple CRUD, a rich
  domain model where the rules are complex.
- A new feature adds a folder; it does not touch five layers.
