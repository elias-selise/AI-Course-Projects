"use client";

import React, { useState } from "react";
import {
  DndContext,
  DragOverlay,
  DragStartEvent,
  DragEndEvent,
  DragOverEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { INITIAL_COLUMNS, Column, CardItem } from "@/types/kanban";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCard } from "@/components/KanbanCard";
import { LayoutGrid, Sparkles } from "lucide-react";

export default function KanbanBoard() {
  const [columns, setColumns] = useState<Column[]>(INITIAL_COLUMNS);
  const [activeCard, setActiveCard] = useState<CardItem | null>(null);
  const [activeColumnId, setActiveColumnId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    })
  );

  const handleRenameColumn = (columnId: string, newTitle: string) => {
    setColumns((prev) =>
      prev.map((col) => (col.id === columnId ? { ...col, title: newTitle } : col))
    );
  };

  const handleAddCard = (columnId: string, title: string, details: string) => {
    const newCard: CardItem = {
      id: `card-${Date.now()}`,
      title,
      details,
    };
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, cards: [...col.cards, newCard] } : col
      )
    );
  };

  const handleDeleteCard = (columnId: string, cardId: string) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId
          ? { ...col, cards: col.cards.filter((c) => c.id !== cardId) }
          : col
      )
    );
  };

  const findColumnOfCard = (cardId: string): Column | undefined => {
    return columns.find((col) => col.cards.some((c) => c.id === cardId));
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const cardId = active.id as string;
    const sourceCol = findColumnOfCard(cardId);
    if (sourceCol) {
      const card = sourceCol.cards.find((c) => c.id === cardId);
      if (card) {
        setActiveCard(card);
        setActiveColumnId(sourceCol.id);
      }
    }
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeCol = findColumnOfCard(activeId);
    let overCol = columns.find((col) => col.id === overId);

    if (!overCol) {
      overCol = findColumnOfCard(overId);
    }

    if (!activeCol || !overCol || activeCol.id === overCol.id) return;

    setColumns((prev) => {
      const sourceCards = [...activeCol.cards];
      const destCards = [...overCol!.cards];

      const activeIndex = sourceCards.findIndex((c) => c.id === activeId);
      const [movedCard] = sourceCards.splice(activeIndex, 1);

      const overIndex = destCards.findIndex((c) => c.id === overId);
      if (overIndex >= 0) {
        destCards.splice(overIndex, 0, movedCard);
      } else {
        destCards.push(movedCard);
      }

      return prev.map((col) => {
        if (col.id === activeCol.id) return { ...col, cards: sourceCards };
        if (col.id === overCol!.id) return { ...col, cards: destCards };
        return col;
      });
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCard(null);
    setActiveColumnId(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeCol = findColumnOfCard(activeId);
    if (!activeCol) return;

    const activeIndex = activeCol.cards.findIndex((c) => c.id === activeId);
    const overIndex = activeCol.cards.findIndex((c) => c.id === overId);

    if (activeIndex !== overIndex && overIndex !== -1) {
      setColumns((prev) =>
        prev.map((col) =>
          col.id === activeCol.id
            ? { ...col, cards: arrayMove(col.cards, activeIndex, overIndex) }
            : col
        )
      );
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-[#032147] text-slate-100 selection:bg-[#ecad0a] selection:text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/60 bg-slate-950/40 px-8 py-5 backdrop-blur-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-tr from-[#753991] to-[#209dd7] p-2.5 shadow-lg shadow-[#753991]/20">
              <LayoutGrid className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                Project Kanban
                <span className="text-xs font-normal text-[#ecad0a] bg-[#ecad0a]/10 px-2 py-0.5 rounded-full border border-[#ecad0a]/30">
                  MVP Single Board
                </span>
              </h1>
              <p className="text-xs text-[#888888]">
                Streamlined workflow management & real-time drag and drop
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-[#888888]">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#ecad0a]" />
              <span>Accent: #ecad0a</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#209dd7]" />
              <span>Primary: #209dd7</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#753991]" />
              <span>Secondary: #753991</span>
            </div>
          </div>
        </div>
      </header>

      {/* Board Content */}
      <div className="flex-1 p-8 overflow-x-auto">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <div className="flex items-start gap-6 pb-6 min-h-[calc(100vh-140px)]">
            {columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                onRenameColumn={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </div>

          <DragOverlay>
            {activeCard && activeColumnId ? (
              <div className="rotate-2 scale-105 transition-transform">
                <KanbanCard
                  card={activeCard}
                  columnId={activeColumnId}
                  onDeleteCard={() => {}}
                />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>
    </main>
  );
}
