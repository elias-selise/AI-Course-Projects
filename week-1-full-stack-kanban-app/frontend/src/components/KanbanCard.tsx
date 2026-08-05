"use client";

import React from "react";
import { Trash2, GripVertical, FileText } from "lucide-react";
import { CardItem } from "@/types/kanban";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { getColumnMeta } from "@/lib/columnMeta";

interface KanbanCardProps {
  card: CardItem;
  columnId: string;
  onDeleteCard: (columnId: string, cardId: string) => void;
}

export function KanbanCard({ card, columnId, onDeleteCard }: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: card.id,
    data: {
      type: "Card",
      card,
      columnId,
    },
  });

  const { icon: ColumnIcon, accent } = getColumnMeta(columnId);

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    borderLeftWidth: 4,
    borderLeftColor: accent,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`group relative rounded-xl border border-slate-700/60 bg-slate-900/80 p-4 shadow-md transition-all hover:border-[#209dd7]/50 hover:shadow-lg hover:shadow-[#209dd7]/10 ${
        isDragging ? "opacity-40 shadow-2xl ring-2 ring-[#ecad0a]" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <button
            {...attributes}
            {...listeners}
            className="cursor-grab text-slate-500 hover:text-slate-300 active:cursor-grabbing focus:outline-none shrink-0"
            aria-label="Drag card"
            type="button"
          >
            <GripVertical className="h-4 w-4" />
          </button>
          <span className="shrink-0 mt-0.5" style={{ color: accent }} aria-hidden>
            <ColumnIcon className="h-3.5 w-3.5" />
          </span>
          <h4 className="font-semibold text-slate-100 text-sm tracking-wide">
            {card.title}
          </h4>
        </div>
        <button
          onClick={() => onDeleteCard(columnId, card.id)}
          className="text-slate-500 opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity p-1 rounded hover:bg-slate-800 shrink-0"
          title="Delete task"
          aria-label={`Delete card ${card.title}`}
          type="button"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {card.details && (
        <p className="mt-2 text-xs text-[#888888] leading-relaxed flex items-start gap-1.5 pl-6">
          <FileText className="h-3 w-3 mt-0.5 shrink-0 opacity-60" aria-hidden />
          <span>{card.details}</span>
        </p>
      )}
    </div>
  );
}
