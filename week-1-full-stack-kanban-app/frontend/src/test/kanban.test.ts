import { describe, it, expect } from "vitest";
import { INITIAL_COLUMNS, Column, CardItem } from "../types/kanban";

describe("Kanban State Mutations", () => {
  it("should initialize with exactly 5 columns", () => {
    expect(INITIAL_COLUMNS).toHaveLength(5);
  });

  it("should add a new card to a column", () => {
    let columns = [...INITIAL_COLUMNS];
    const columnId = "col-backlog";
    const newCard: CardItem = {
      id: "test-card-1",
      title: "New Test Task",
      details: "Test Details",
    };

    columns = columns.map((col) =>
      col.id === columnId ? { ...col, cards: [...col.cards, newCard] } : col
    );

    const backlogCol = columns.find((c) => c.id === columnId);
    expect(backlogCol?.cards).toContainEqual(newCard);
  });

  it("should delete a card from a column", () => {
    let columns = [...INITIAL_COLUMNS];
    const columnId = "col-backlog";
    const targetCardId = "card-1";

    columns = columns.map((col) =>
      col.id === columnId
        ? { ...col, cards: col.cards.filter((c) => c.id !== targetCardId) }
        : col
    );

    const backlogCol = columns.find((c) => c.id === columnId);
    expect(backlogCol?.cards.some((c) => c.id === targetCardId)).toBe(false);
  });

  it("should rename a column title", () => {
    let columns = [...INITIAL_COLUMNS];
    const columnId = "col-backlog";
    const newTitle = "Upcoming Tasks";

    columns = columns.map((col) =>
      col.id === columnId ? { ...col, title: newTitle } : col
    );

    const backlogCol = columns.find((c) => c.id === columnId);
    expect(backlogCol?.title).toBe(newTitle);
  });
});
