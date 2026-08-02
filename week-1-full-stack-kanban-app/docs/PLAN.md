# Project Implementation Plan & Verification Checklist

## Part 1: Plan & Frontend Documentation
- [x] Document the existing frontend structure in [`frontend/AGENTS.md`](file:///mnt/5cf2a800-97fa-463a-878d-37bb8b42ecdb/LLMpractice/AI%20Course%20Projects/week-1-full-stack-kanban-app/frontend/AGENTS.md).
- [x] Enrich [`docs/PLAN.md`](file:///mnt/5cf2a800-97fa-463a-878d-37bb8b42ecdb/LLMpractice/AI%20Course%20Projects/week-1-full-stack-kanban-app/docs/PLAN.md) into a granular task list with test verification steps.
- [x] Obtain user approval on the implementation plan.

---

## Part 2: Backend Scaffolding & Container Infrastructure
- [x] Create Python backend structure under `backend/` using `uv`.
- [x] Create `Dockerfile` packaging Next.js build + FastAPI serving statically at `/`.
- [x] Create cross-platform shell/batch launch scripts in `scripts/` (`start.sh`, `stop.sh`, `start.bat`, `stop.bat`, etc.).
- [x] **Tests & Success Criteria**:
  - `curl http://localhost:8000/api/health` returns `200 OK` JSON `{ "status": "ok" }`.
  - Static HTML "Hello World" serves cleanly at `/`.

---

## Part 3: Static Frontend Export & Integration
- [x] Configure `next.config.ts` for static HTML export (`output: 'export'`).
- [x] Build frontend and serve built static assets from FastAPI `StaticFiles`.
- [x] **Tests & Success Criteria**:
  - `npm run test` passes unit tests.
  - `npm run test:e2e` passes Playwright UI tests.
  - Navigating to `http://localhost:8000/` displays the full static Kanban demo board.

---

## Part 4: Fake User Sign-in Experience
- [x] Add auth API route `/api/login` accepting `user` / `password`.
- [x] Store session/token in secure cookie or local storage.
- [x] Show login form when unauthenticated; show Kanban board when authenticated. Add logout functionality.
- [x] **Tests & Success Criteria**:
  - Invalid login returns `401 Unauthorized`.
  - Credentials `user` / `password` grant access and redirect to the Kanban view.

---

## Part 5: Database Schema & Modeling
- [x] Design JSON/SQLite database schema for Users, Boards, Columns, and Cards (1 board per user).
- [x] Create design document `docs/DATABASE.md` detailing tables and relations.
- [x] **Tests & Success Criteria**:
  - User sign-off obtained on database schema design.

---

## Part 6: Backend CRUD Endpoints & Auto-Migration
- [x] Setup SQLite database auto-creation if file does not exist.
- [x] Create FastAPI endpoints:
  - `GET /api/board`
  - `PUT /api/board` / `POST /api/cards` / `PUT /api/cards/{id}` / `DELETE /api/cards/{id}`
- [x] **Tests & Success Criteria**:
  - pytest test suite verifies CRUD persistence and schema integrity.

---

## Part 7: Full Stack Integration (Frontend + Backend)
- [ ] Connect frontend state/hooks to backend API endpoints instead of static mock data.
- [ ] Ensure drag-and-drop actions, card creation, and edits sync seamlessly to backend.
- [ ] **Tests & Success Criteria**:
  - Page refresh preserves moved cards and column updates.

---

## Part 8: AI OpenRouter Connectivity Verification
- [ ] Setup `OPENROUTER_API_KEY` configuration and HTTP client in backend.
- [ ] Implement simple `/api/ai/test` endpoint performing a "2+2" prompt to `openai/gpt-oss-120b`.
- [ ] **Tests & Success Criteria**:
  - Endpoint returns a valid LLM response string containing `"4"`.

---

## Part 9: AI Structured Output Engine
- [ ] Build LLM context payload builder (Kanban state JSON + User question + History).
- [ ] Implement OpenRouter Structured Outputs request parsing (response message + optional board JSON).
- [ ] **Tests & Success Criteria**:
  - Backend unit tests simulate AI mutations and confirm schema validity of returned Kanban board.

---

## Part 10: AI Chat Sidebar & Dynamic Board Refresh
- [ ] Add AI chat sidebar component in frontend.
- [ ] Implement streaming or async polling for chat messages.
- [ ] Automatically re-render Kanban board when AI structured output contains an updated board.
- [ ] **Tests & Success Criteria**:
  - User can ask "Move task X to Done" and the board visually updates without manual reload.

