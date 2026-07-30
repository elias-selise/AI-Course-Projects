'use client'

import { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Card } from '../lib/types'
import { useBoard } from '../lib/board-context'

interface Props {
  card: Card
  columnId: string
}

export function KanbanCard({ card, columnId }: Props) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(card.title)
  const [details, setDetails] = useState(card.details)
  const { dispatch } = useBoard()

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: card.id,
    data: { type: 'card', columnId },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  }

  function handleSave() {
    if (title.trim()) {
      dispatch({ type: 'EDIT_CARD', cardId: card.id, title: title.trim(), details })
    }
    setEditing(false)
  }

  function handleCancel() {
    setTitle(card.title)
    setDetails(card.details)
    setEditing(false)
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="group bg-white rounded-lg border border-zinc-200 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="p-3">
        {editing ? (
          <div className="space-y-2" onClick={e => e.stopPropagation()}>
            <input
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full px-2 py-1 text-sm font-medium border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
              onKeyDown={e => { if (e.key === 'Enter') handleSave(); if (e.key === 'Escape') handleCancel() }}
            />
            <textarea
              value={details}
              onChange={e => setDetails(e.target.value)}
              className="w-full px-2 py-1 text-xs text-zinc-600 border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
              onKeyDown={e => { if (e.key === 'Escape') handleCancel() }}
            />
            <div className="flex gap-1">
              <button onClick={handleSave} className="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700">Save</button>
              <button onClick={handleCancel} className="px-2 py-1 text-xs font-medium text-zinc-600 bg-zinc-100 rounded hover:bg-zinc-200">Cancel</button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-start justify-between gap-2">
              <h3
                className="text-sm font-semibold text-zinc-800 cursor-pointer flex-1"
                onClick={() => setEditing(true)}
                {...attributes}
                {...listeners}
              >
                {card.title}
              </h3>
              <button
                onClick={() => dispatch({ type: 'DELETE_CARD', cardId: card.id })}
                className="opacity-0 group-hover:opacity-100 p-0.5 text-zinc-400 hover:text-red-500 transition-opacity"
                aria-label="Delete card"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
                  <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
            {card.details && (
              <p className="mt-1 text-xs text-zinc-500 line-clamp-2">{card.details}</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
