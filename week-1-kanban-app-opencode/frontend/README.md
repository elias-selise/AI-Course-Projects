# Kanban Board

A client-rendered Kanban-style project management board built with Next.js.

## Features

- Single board with 5 columns (renamable by clicking the title)
- Cards with title and details (click to edit inline)
- Drag and drop cards between columns
- Add new cards to any column
- Delete existing cards
- Pre-populated with 10 dummy cards
- No persistence, no user management, no extra features

## Tech Stack

- Next.js 16 (App Router, client-rendered)
- React 19 + TypeScript
- Tailwind CSS 4
- @dnd-kit (drag and drop)
- Vitest (unit tests)
- Playwright (e2e tests)

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Production build |
| `npm start` | Start production server |
| `npm test` | Run unit tests |
| `npm run test:e2e` | Run Playwright integration tests |
| `npm run lint` | Run ESLint |

## Tests

- **Unit tests** (Vitest): 6 tests covering the board reducer (add, delete, move, rename, edit)
- **E2E tests** (Playwright): 6 tests covering all user flows (render, add card, delete card, rename column, edit card)
