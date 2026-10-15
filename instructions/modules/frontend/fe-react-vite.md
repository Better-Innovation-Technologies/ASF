## Frontend — React + TypeScript (Vite)

| | |
|---|---|
| Framework | React {{react_version}} + TypeScript (strict), built with Vite |
| Runtime for tooling | Node.js {{node_version}} |
| Server state | TanStack Query — no manual fetching in `useEffect` |
| Global UI state | Zustand — never server data in the UI store |
| Validation | Zod at the API boundary |
| Tests | Vitest + React Testing Library |

### Module structure

```
{{fe_src_path}}/
├── components/
│   ├── ui/            # base components (Button, Modal, Badge…)
│   └── domain/        # domain-specific components
├── pages/             # page-level components
├── hooks/             # custom hooks — reusable logic
├── services/          # API calls — the backend is called only from here
├── types/             # shared TypeScript types
├── utils/             # pure functions, helpers
└── stores/            # global UI state
```

### Conventions

- Components `PascalCase` (`EntityCard.tsx`), hooks `useXxx`, services `xxxService`, constants
  `UPPER_SNAKE_CASE`.
- `strict` mode on — no `any` without a comment explaining it; every component has typed props.
- Accessibility is part of done: semantic elements, labels, keyboard navigation, focus states.
