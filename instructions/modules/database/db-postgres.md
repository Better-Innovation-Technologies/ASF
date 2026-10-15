## Database — PostgreSQL

PostgreSQL {{postgres_version}}.

### Naming association tables

`<<TableName1>><<TableName2>>Link` — e.g. `ProcessTechnologyLink`, `UserOrganizationLink`.

### Rules

- Every foreign key is declared in the ORM schema (relation + constraint). An `*_id` column without
  a declared relation is a blocking violation.
- No N+1 queries — eager loading or aggregate queries.
- Explicit transactions for multi-step operations.
- Migrations are versioned, reviewed, reversible where possible, and never destructive without an
  accompanying data migration.
- Every significant query has a verified index; `EXPLAIN` is attached to the merge request when a
  query on a large table changes.
- Timestamps are `timestamptz`, stored in UTC.
