## Principles (non-negotiable)

| Principle | In practice |
|---|---|
| **KISS** | The simplest thing that works. No speculative abstraction. |
| **DRY** | One implementation per piece of logic. Duplication is a bug waiting. |
| **YAGNI** | Implement nothing that is not in the current `task.md`. |
| **SOLID** | One module, one responsibility. Compose rather than modify. |
| **12-Factor** | Config from the environment. Stateless processes. Logs to stdout. No secrets in git. |
| **Fail Fast** | No `catch(e) {}` / `except: pass`. No silent fallbacks. |
| **Explicit over implicit** | When something is missing → throw/raise, do not guess. |

### Hard-coded values — forbidden in business logic

Every fixed set of values must be expressed as:
- **TypeScript:** an `enum`, an `as const` object, or a union type in `<domain>.types.ts`
- **Python:** an `Enum` (from `enum.Enum`) or a constant in `core/constants.py`

Do not use magic strings or literal numbers in application logic.

```typescript
// CORRECT
enum EntityStatus { DRAFT = 'DRAFT', ACTIVE = 'ACTIVE', CLOSED = 'CLOSED' }

// WRONG
if (entity.status === 'active') { ... }
```

### Explicit DTOs — no inline anonymous objects

Every object passed between layers must have an explicitly declared type or schema.

```typescript
// CORRECT
const response: EntityResponseDto = mapToDto(entity);
return response;

// WRONG
return { id: entity.id, name: entity.name };  // no declared type
```

### Co-locate schemas and types with the module

Zod schemas, TypeScript interfaces, classes and enums belong in the module's own files
(`<domain>.schema.ts` / `<domain>.types.ts`). Do not scatter them into generic files outside
the module.

### Anti-patterns to avoid

- **`console.log` / `print` in production** → logger with `traceId` / `trace_id`
- **Magic strings / literal numbers** → typed enums or constants
- **Inline anonymous objects between layers** → an explicitly declared DTO or type
- **Orphan FKs in the ORM schema** → every `*_id` has its relation declared
- **Schemas, interfaces or enums outside the module** → co-location is mandatory
- **Fat controllers/routers** → business logic belongs in services
- **Unjustified `Any`** → strict typecheck blocks CI
- **Silently swallowed exceptions** → every catch/except logs or re-raises
- **Secrets in code** → environment variables through config
- **Order-dependent tests** → every test isolated
- **Mocking the DB in integration tests** → use a real database
