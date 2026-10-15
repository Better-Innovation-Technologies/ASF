## Backend for frontend — Next.js route handlers

The BFF is the only backend the browser talks to: it holds the session, enforces authorization and
calls the core services on the browser's behalf.

- Route handlers under `src/app/api/**/route.ts`; one file per resource, verbs as exported functions.
- **Authorization first**: every handler resolves the session and checks the action against the
  role matrix before calling anything.
- The BFF forwards; it does not own domain logic. Business rules live in the core service.
- Errors from the core are passed through with their cause, context and action, never swallowed.
- The public contract is in `openapi.yaml` and a test fails when a route has no documented case.
