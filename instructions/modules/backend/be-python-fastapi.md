## Backend — Python + FastAPI

| | |
|---|---|
| Language | Python {{python_version}} |
| Framework | FastAPI (async where the I/O is async) |
| ORM / migrations | SQLAlchemy 2.x (typed `Mapped[...]`) + Alembic |
| Validation | Pydantic 2 at the API boundary |
| Tests | pytest |
| Type check / lint | mypy (strict) · ruff — both block CI |

- Code under `{{be_modules_path}}/`; one package per domain module.
- Routers are thin: validation via Pydantic models, then a service call.
- Every FK column is declared with `ForeignKey()` and a `relationship()`; migrations are reviewed
  and never destructive without a data migration.
- Configuration through a settings object read from the environment; nothing read from
  `os.environ` in business code.
- The logger is configured once in `{{be_logger_path}}`; `print()` only in scripts and tests.
