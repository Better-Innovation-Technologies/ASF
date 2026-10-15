## Code style — Python

- Formatting and linting with **ruff** (`ruff format`, `ruff check`), line length {{line_length}};
  type checking with **mypy** in strict mode. Both block CI, with a ratchet for existing debt.
- Type hints on every public function; no `Any` without a comment explaining why.
- `snake_case` functions and variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.
- Prefer small pure functions and dataclasses / Pydantic models over dicts passed around.
- No bare `except:` and no `except Exception: pass`; catch what you can handle, re-raise the rest.
