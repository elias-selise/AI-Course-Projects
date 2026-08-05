"use client";

import React, { useState } from "react";
import { Plus, Edit2, Check, X } from "lucide-react";
import { Column } from "@/types/kanban";
import { KanbanCard } from "./KanbanCard";
import { getColumnMeta } from "@/lib/columnMeta";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useDroppable } from "@dnd-kit/core";

interface KanbanColumnProps {
  column: Column;
  onRenameColumn: (columnId: string, newTitle: string) => void;
  onAddCard: (columnId: string, title: string, details: string) => void;
  onDeleteCard: (columnId: string, cardId: string) => void;
}

export function KanbanColumn({
  column,
  onRenameColumn,
  onAddCard,
  onDeleteCard,
}: KanbanColumnProps) {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(column.title);
  const [isAddingCard, setIsAddingCard] = useState(false);
  const [newCardTitle, setNewCardTitle] = useState("");
  const [newCardDetails, setNewCardDetails] = useState("");

  const { setNodeRef } = useDroppable({
    id: column.id,
    data: {
      type: "Column",
      column,
    },
  });

  const { icon: ColumnIcon, accent, chipBg } = getColumnMeta(column.id);

  const handleTitleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (titleInput.trim()) {
      onRenameColumn(column.id, titleInput.trim());
      setIsEditingTitle(false);
    }
  };

  const handleAddCardSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newCardTitle.trim()) {
      onAddCard(column.id, newCardTitle.trim(), newCardDetails.trim());
      setNewCardTitle("");
      setNewCardDetails("");
      setIsAddingCard(false);
    }
  };

  return (
    <div
      ref={setNodeRef}
      className="flex flex-col rounded-2xl border border-slate-700/50 bg-slate-900/60 p-4 shadow-xl backdrop-blur-md min-w-[280px] w-80 flex-shrink-0"
    >
      {/* Column Header */}
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-3 mb-4">
        {isEditingTitle ? (
          <form
            onSubmit={handleTitleSubmit}
            className="flex items-center gap-1 w-full"
          >
            <input
              type="text"
              value={titleInput}
              onChange={(e) => setTitleInput(e.target.value)}
              className="w-full rounded bg-slate-800 px-2 py-1 text-sm font-semibold text-slate-100 border border-[#209dd7] focus:outline-none"
              autoFocus
            />
            <button
              type="submit"
              className="p-1 text-green-400 hover:text-green-300"
              title="Save"
            >
              <Check className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => {
                setTitleInput(column.title);
                setIsEditingTitle(false);
              }}
              className="p-1 text-slate-400 hover:text-slate-200"
              title="Cancel"
            >
              <X className="h-4 w-4" />
            </button>
          </form>
        ) : (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2">
              <span
                className="grid h-7 w-7 place-items-center rounded-lg border border-slate-700/60"
                style={{ backgroundColor: chipBg, color: accent }}
              >
                <ColumnIcon className="h-4 w-4" />
              </span>
              <h3 className="font-bold text-[#032147] text-base bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
                {column.title}
              </h3>
              <span className="ml-1 rounded-full bg-slate-800 px-2 py-0.5 text-xs text-[#888888]">
                {column.cards.length}
              </span>
            </div>
            <button
              onClick={() => setIsEditingTitle(true)}
              className="p-1 text-slate-400 hover:text-[#209dd7] transition-colors rounded"
              title="Rename column"
              aria-label="Rename column"
              type="button"
            >
              <Edit2 className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Cards List */}
      <SortableContext
        items={column.cards.map((c) => c.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="flex-1 space-y-3 overflow-y-auto pr-1 min-h-[120px]">
          {column.cards.map((card) => (
            <KanbanCard
              key={card.id}
              card={card}
              columnId={column.id}
              onDeleteCard={onDeleteCard}
            />
          ))}
          {column.cards.length === 0 && (
            <div className="h-24 rounded-xl border border-dashed border-slate-700/50 flex flex-col items-center justify-center gap-1.5 text-xs text-slate-500">
              <ColumnIcon className="h-5 w-5 opacity-40" />
              <span>Drop items here</span>
            </div>
          )}
        </div>
      </SortableContext>

      {/* Add Card Section */}
      <div className="mt-4 pt-3 border-t border-slate-700/50">
        {isAddingCard ? (
          <form onSubmit={handleAddCardSubmit} className="space-y-3">
            <input
              type="text"
              placeholder="Task title..."
              value={newCardTitle}
              onChange={(e) => setNewCardTitle(e.target.value)}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-[#753991] focus:outline-none"
              autoFocus
              required
            />
            <textarea
              placeholder="Details (optional)..."
              value={newCardDetails}
              onChange={(e) => setNewCardDetails(e.target.value)}
              rows={2}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-[#753991] focus:outline-none resize-none"
            />
            <div className="flex items-center gap-2">
              <button
                type="submit"
                className="flex-1 rounded-lg bg-[#753991] hover:bg-[#8e45af] px-3 py-1.5 text-xs font-semibold text-white transition-colors"
              >
                Add Card
              </button>
              <button
                type="button"
                onClick={() => setIsAddingCard(false)}
                className="rounded-lg bg-slate-800 hover:bg-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setIsAddingCard(true)}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700 bg-slate-900/40 py-2 text-xs font-medium text-[#209dd7] hover:bg-slate-800/60 transition-colors"
            type="button"
          >
            <Plus className="h-4 w-4" />
            <span>Add Card</span>
          </button>
        )}
      </div>
    </div>
  );
}
