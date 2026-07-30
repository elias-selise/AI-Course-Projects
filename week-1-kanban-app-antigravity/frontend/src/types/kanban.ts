export interface CardItem {
  id: string;
  title: string;
  details: string;
}

export interface Column {
  id: string;
  title: string;
  cards: CardItem[];
}

export const INITIAL_COLUMNS: Column[] = [
  {
    id: "col-backlog",
    title: "Backlog",
    cards: [
      {
        id: "card-1",
        title: "User Authentication",
        details: "Explore OAuth2 and JWT implementations for future login phase.",
      },
      {
        id: "card-2",
        title: "Analytics Integration",
        details: "Identify key events to track user engagement across boards.",
      },
    ],
  },
  {
    id: "col-todo",
    title: "To Do",
    cards: [
      {
        id: "card-3",
        title: "Design System Tokens",
        details: "Define CSS custom variables for accent yellow, primary blue, and purple.",
      },
      {
        id: "card-4",
        title: "Drag and Drop Spec",
        details: "Ensure smooth touch and desktop dragging experiences using dnd-kit.",
      },
    ],
  },
  {
    id: "col-in-progress",
    title: "In Progress",
    cards: [
      {
        id: "card-5",
        title: "Kanban Board UI",
        details: "Build modern glassmorphic UI components with standard layout constraints.",
      },
    ],
  },
  {
    id: "col-review",
    title: "Review",
    cards: [
      {
        id: "card-6",
        title: "Accessibility Audit",
        details: "Verify ARIA roles and keyboard focus management across interactive elements.",
      },
    ],
  },
  {
    id: "col-done",
    title: "Done",
    cards: [
      {
        id: "card-7",
        title: "Project Setup",
        details: "NextJS 15 workspace initialization with Tailwind CSS styling.",
      },
    ],
  },
];
