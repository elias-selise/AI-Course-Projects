# The Project Management MVP Web App

## Business Requirements

This project is building a Project Management App.

### Key Features

- A user can sign in.
- When signed in, the user sees a Kanban board representing their project.
- The Kanban board has fixed columns that can be renamed.
- The cards on the Kanban board can be moved with drag and drop, and edited.
- There is an AI chat feature in a sidebar; the AI is able to create, edit, and move one or more cards.

---

## Limitations

For the MVP:

- There will only be a user sign in (hardcoded to `user` and `password`), but the database will support multiple users in the future.
- There will only be **1 Kanban board** per signed-in user.
- The application will run locally in a Docker container.

---

## Technical Decisions

- Next.js frontend
- Python FastAPI backend, including serving the static Next.js site at `/`
- Everything packaged into a Docker container
- Use **uv** as the package manager for Python in the Docker container
- Use **OpenRouter** for AI calls (`OPENROUTER_API_KEY` is stored in the project root `.env`)
- Use `openai/gpt-oss-120b` as the model
- Use a local SQLite database, creating a new database if one doesn't exist
- Provide start and stop server scripts for macOS, Windows, and Linux in the `scripts/` directory

---

# Starting Point

A working MVP of the frontend has already been built in the `frontend` directory.

It is **not yet** designed for the Docker setup and is currently a pure frontend-only demo.

---

# Color Scheme

| Purpose | Color |
|---------|-------|
| Accent Yellow | `#ecad0a` — Accent lines, highlights |
| Blue Primary | `#209dd7` — Links, key sections |
| Purple Secondary | `#753991` — Submit buttons, important actions |
| Dark Navy | `#032147` — Main headings |
| Gray Text | `#888888` — Supporting text, labels |

---

# Coding Standards

1. Use the latest versions of libraries and idiomatic approaches available today.
2. Keep it simple:
   - Never over-engineer.
   - Always simplify.
   - No unnecessary defensive programming.
   - No extra features.
   - Focus on simplicity.
3. Be concise.
   - Keep the `README` minimal.
   - **No emojis.**
4. When encountering issues:
   - Identify the root cause before attempting a fix.
   - Do not guess.
   - Prove the root cause with evidence.
   - Then fix the root cause.

---

# Working Documentation

All documents for planning and executing this project will be located in the `docs/` directory.

Please review:

- `docs/PLAN.md`

before proceeding.
