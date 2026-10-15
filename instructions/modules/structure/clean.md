## Internal structure — clean architecture

Concentric rings, dependencies pointing **inwards only**:

1. **Entities** — enterprise rules, pure code.
2. **Use cases** — application rules; one class/function per use case, with its input and output
   models.
3. **Interface adapters** — controllers, presenters, gateways, repositories' implementations.
4. **Frameworks and drivers** — web framework, ORM, external SDKs: kept at the edge.

- Nothing in an inner ring knows a name declared in an outer ring.
- Data crossing a boundary is a plain DTO declared by the inner ring, never an ORM entity or an
  HTTP request object.
- Use cases are tested without frameworks; the outer rings are tested with integration tests.
