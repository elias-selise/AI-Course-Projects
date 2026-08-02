# Database Architecture & Schema Specification

## Overview
The application uses SQLite as its primary relational store. Each signed-in user has **1 Kanban board**.

---

## Schema Definition (JSON Representation)

```json
{
  "users": [
    {
      "id": "user-1",
      "username": "user",
      "password_hash": "password"
    }
  ],
  "boards": [
    {
      "id": "board-user-1",
      "user_id": "user-1",
      "title": "Project Kanban Board",
      "columns": [
        {
          "id": "backlog",
          "title": "Backlog",
          "order": 0,
          "cards": [
            {
              "id": "card-1",
              "title": "Project Setup",
              "details": "NextJS 15 workspace initialization with Tailwind CSS styling.",
              "order": 0
            }
          ]
        },
        {
          "id": "todo",
          "title": "To Do",
          "order": 1,
          "cards": []
        },
        {
          "id": "in-progress",
          "title": "In Progress",
          "order": 2,
          "cards": []
        },
        {
          "id": "review",
          "title": "Review",
          "order": 3,
          "cards": []
        },
        {
          "id": "done",
          "title": "Done",
          "order": 4,
          "cards": []
        }
      ]
    }
  ]
}
```

---

## SQLite Tables Definition

### `users` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique user identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Username |
| `password` | TEXT | NOT NULL | Password |

### `boards` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Board identifier |
| `user_id` | TEXT | FOREIGN KEY (users.id), NOT NULL | Owner user ID |
| `data` | TEXT | NOT NULL | Complete Kanban board JSON structure |
