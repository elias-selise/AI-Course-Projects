<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Frontend Codebase Architecture & Guidelines

## Tech Stack Overview
- **Framework**: Next.js 16 (App Router)
- **UI & React**: React 19, Lucide React (icons), canvas-confetti
- **Drag and Drop**: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- **Styling**: Tailwind CSS v4, `clsx`, `tailwind-merge`
- **Testing**: Vitest (`npm run test`), Playwright (`npm run test:e2e`)

## Project Structure (`src/`)
- `src/app`: Page components and Next.js App Router layouts.
- `src/components`: UI components including Kanban board columns, cards, and AI sidebar interface.
- `src/types`: TypeScript definitions for board state, cards, columns, and AI message payload structures.
- `src/test`: Setup and unit tests for React components.

## Available Scripts
- `npm run dev`: Launch standard Next.js development server.
- `npm run build`: Compile and build static export or application bundle.
- `npm run test`: Run unit tests using Vitest.
- `npm run test:e2e`: Execute end-to-end tests using Playwright.
