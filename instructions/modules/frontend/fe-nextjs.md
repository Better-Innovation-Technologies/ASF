## Frontend — Next.js (App Router) + TypeScript

| | |
|---|---|
| Framework | Next.js {{next_version}} App Router, React Server Components, TypeScript strict |
| Data | server components and route handlers read data; client components only for interactivity |
| Validation | Zod at every boundary (forms, route handlers, external APIs) |
| Tests | Vitest + React Testing Library; Playwright for flows |

- Default to **server components**; add `"use client"` only where state or browser APIs are needed,
  as low in the tree as possible.
- Secrets and server-only modules never reach a client component (`server-only` guard).
- Data mutations go through server actions or route handlers with validation and authorization —
  never trust the client.
- Source under `{{fe_src_path}}/app` (routes), `components/`, `lib/` (server and shared helpers).
