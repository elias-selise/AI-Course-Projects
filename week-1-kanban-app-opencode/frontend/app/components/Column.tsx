'use client'

import { useState, useCallback } from 'react'
import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { KanbanCard } from './KanbanCard'
import { AddCardForm } from './AddCardForm'
import { Column as ColumnType } from '../lib/types'
import { useBoard } from '../lib/board-context'

interface Props {
  column: ColumnType
}

export function Column({ column }: Props) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(column.title)
  const { state, dispatch } = useBoard()

  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
    data: { type: 'column' },
  })

  const handleRename = useCallback(() => {
    if (title.trim() && title.trim() !== column.title) {
      dispatch({ type: 'RENAME_COLUMN', columnId: column.id, title: title.trim() })
    } else {
      setTitle(column.title)
    }
    setEditing(false)
  }, [title, column.id, column.title, dispatch])

  return (
    <div className="flex-shrink-0 w-72 flex flex-col bg-zinc-50 rounded-xl">
      <div
        className={`px-3 py-3 border-b ${isOver ? 'border-blue-400' : 'border-zinc-200'} transition-colors`}
      >
        {editing ? (
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            className="w-full px-2 py-1 text-sm font-bold border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
            onBlur={handleRename}
            onKeyDown={e => {
              if (e.key === 'Enter') handleRename()
              if (e.key === 'Escape') { setTitle(column.title); setEditing(false) }
            }}
          />
        ) : (
          <button
            onClick={() => setEditing(true)}
            className="w-full text-left group flex items-center justify-between"
          >
            <h2 className="text-sm font-bold text-zinc-700 uppercase tracking-wider">{column.title}</h2>
            <span className="text-xs text-zinc-400 bg-zinc-200 rounded-full px-2 py-0.5 font-medium">
              {column.cardIds.length}
            </span>
          </button>
        )}
      </div>

      <div
        ref={setNodeRef}
        className={`flex-1 p-2 space-y-2 min-h-[120px] transition-colors rounded-b-xl ${isOver ? 'bg-blue-50/50' : ''}`}
      >
        <SortableContext items={column.cardIds} strategy={verticalListSortingStrategy}>
          {column.cardIds.map(cardId => {
            const card = state.cards[cardId]
            if (!card) return null
            return <KanbanCard key={card.id} card={card} columnId={column.id} />
          })}
        </SortableContext>
        <AddCardForm columnId={column.id} />
      </div>
    </div>
  )
}
