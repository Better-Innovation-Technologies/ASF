## Backend — TypeScript + Node.js

| | |
|---|---|
| Runtime | Node.js {{node_version}} (LTS), ES modules |
| Language | TypeScript, `strict` on — `tsc --noEmit` blocks CI |
| Framework | {{be_framework}} |
| ORM / migrations | {{be_orm}} |
| Validation | Zod at every boundary (HTTP, queues, env) |
| Tests | Vitest (unit and integration) |

- Code under `{{be_modules_path}}/`; one folder per domain module.
- Handlers are thin: parse with Zod, call a service, map the result to a declared DTO.
- Every relation is declared in the ORM schema; an `*_id` field without a relation is a blocking
  violation.
- Configuration is parsed once at startup with a Zod schema; the process refuses to start on a
  missing variable.
- The logger is configured once in `{{be_logger_path}}`; `console.log` only in scripts and tests.
- Async all the way: no sync I/O in request paths, every promise awaited or explicitly handled.
