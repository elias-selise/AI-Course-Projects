"use client";

import React, { useState, useEffect } from "react";
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
import { LoginForm } from "@/components/LoginForm";
import { AiChatSidebar } from "@/components/AiChatSidebar";
import { LayoutGrid, LogOut, BarChart3, ListChecks } from "lucide-react";

export default function KanbanBoard() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [columns, setColumns] = useState<Column[]>(INITIAL_COLUMNS);
  const [activeCard, setActiveCard] = useState<CardItem | null>(null);
  const [activeColumnId, setActiveColumnId] = useState<string | null>(null);

  const fetchBoard = async () => {
    try {
      const res = await fetch("/api/board");
      if (res.ok) {
        const data = await res.json();
        if (data.columns && Array.isArray(data.columns)) {
          setColumns(data.columns);
        }
      }
    } catch (err) {
      console.error("Failed to fetch board state", err);
    }
  };

  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch("/api/me");
        if (res.ok) {
          const data = await res.json();
          if (data.authenticated) {
            setIsAuthenticated(true);
            fetchBoard();
            return;
          }
        }
      } catch (err) {
        // Fallback to client-side storage state
      }
      const localAuth = localStorage.getItem("kanban_authenticated") === "true";
      setIsAuthenticated(localAuth);
      if (localAuth) {
        fetchBoard();
      }
    }
    checkAuth();
  }, []);

  const saveBoard = async (newColumns: Column[]) => {
    setColumns(newColumns);
    try {
      await fetch("/api/board", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ columns: newColumns }),
      });
    } catch (err) {
      console.error("Failed to save board state", err);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch("/api/logout", { method: "POST" });
    } catch (e) {
      // ignore
    }
    localStorage.removeItem("kanban_authenticated");
    setIsAuthenticated(false);
  };

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    })
  );

  const handleRenameColumn = (columnId: string, newTitle: string) => {
    const updated = columns.map((col) =>
      col.id === columnId ? { ...col, title: newTitle } : col
    );
    saveBoard(updated);
  };

  const handleAddCard = (columnId: string, title: string, details: string) => {
    const newCard: CardItem = {
      id: `card-${Date.now()}`,
      title,
      details,
    };
    const updated = columns.map((col) =>
      col.id === columnId ? { ...col, cards: [...col.cards, newCard] } : col
    );
    saveBoard(updated);
  };

  const handleDeleteCard = (columnId: string, cardId: string) => {
    const updated = columns.map((col) =>
      col.id === columnId
        ? { ...col, cards: col.cards.filter((c) => c.id !== cardId) }
        : col
    );
    saveBoard(updated);
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

    const updated = columns.map((col) => {
      if (col.id === activeCol.id) return { ...col, cards: sourceCards };
      if (col.id === overCol!.id) return { ...col, cards: destCards };
      return col;
    });
    setColumns(updated);
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
      const updated = columns.map((col) =>
        col.id === activeCol.id
          ? { ...col, cards: arrayMove(col.cards, activeIndex, overIndex) }
          : col
      );
      saveBoard(updated);
    } else {
      saveBoard(columns);
    }
  };

  if (isAuthenticated === null) {
    return <div className="min-h-screen bg-[#032147]" />;
  }

  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <main className="h-screen w-screen flex flex-col bg-[#032147] text-slate-100 selection:bg-[#ecad0a] selection:text-slate-900 overflow-hidden">
      {/* Header */}
      <header className="shrink-0 border-b border-slate-700/60 bg-slate-950/40 px-8 py-4 backdrop-blur-lg">
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
          <div className="flex items-center gap-3 text-xs text-[#888888]">
            <div className="hidden md:flex items-center gap-3">
              <span className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-1.5">
                <ListChecks className="h-3.5 w-3.5 text-[#209dd7]" />
                {columns.length} columns
              </span>
              <span className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-1.5">
                <BarChart3 className="h-3.5 w-3.5 text-[#ecad0a]" />
                {columns.reduce((n, c) => n + c.cards.length, 0)} cards
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300 hover:border-red-500/50 hover:bg-red-500/10 hover:text-red-400 transition-colors"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>Log out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container with Board and AI Sidebar */}
      <div className="flex flex-1 min-h-0 overflow-hidden relative">
        {/* Board Content */}
        <div className="flex-1 p-6 overflow-x-auto overflow-y-hidden">
          <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragOver={handleDragOver}
            onDragEnd={handleDragEnd}
          >
            <div className="flex items-start gap-6 h-full pb-2">
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

        {/* AI Sidebar */}
        <AiChatSidebar onBoardUpdated={(newBoard) => setColumns(newBoard)} />
      </div>
    </main>
  );
}
