'use client'

import { useState } from 'react'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
  DragOverEvent,
} from '@dnd-kit/core'
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable'
import { Column } from './Column'
import { useBoard } from '../lib/board-context'
import { Card } from '../lib/types'
import { KanbanCard } from './KanbanCard'


export function Board() {
  const { state, dispatch } = useBoard()
  const [activeCard, setActiveCard] = useState<Card | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  function findColumnOfCard(cardId: string): string | undefined {
    return state.columns.find(col => col.cardIds.includes(cardId))?.id
  }

  function handleDragStart(event: DragStartEvent) {
    const { active } = event
    const card = state.cards[active.id as string]
    if (card) setActiveCard(card)
  }

  function handleDragOver(event: DragOverEvent) {
    const { active, over } = event
    if (!over) return

    const activeId = active.id as string
    const overId = over.id as string

    const activeColId = findColumnOfCard(activeId)
    let targetColId: string | undefined

    if (over.data.current?.type === 'column') {
      targetColId = overId
    } else {
      targetColId = findColumnOfCard(overId)
    }

    if (!activeColId || !targetColId || activeColId === targetColId) return

    const targetCol = state.columns.find(c => c.id === targetColId)
    if (!targetCol) return

    const targetIndex = targetCol.cardIds.indexOf(overId)

    dispatch({
      type: 'MOVE_CARD',
      cardId: activeId,
      sourceColId: activeColId,
      targetColId,
      targetIndex: targetIndex >= 0 ? targetIndex : targetCol.cardIds.length,
    })
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    setActiveCard(null)

    if (!over) return

    const activeId = active.id as string
    const overId = over.id as string

    if (activeId === overId) return

    const activeColId = findColumnOfCard(activeId)
    let targetColId: string | undefined

    if (over.data.current?.type === 'column') {
      targetColId = overId
    } else {
      targetColId = findColumnOfCard(overId)
    }

    if (!activeColId || !targetColId) return

    if (activeColId === targetColId) {
      const col = state.columns.find(c => c.id === activeColId)
      if (!col) return
      const oldIndex = col.cardIds.indexOf(activeId)
      const newIndex = col.cardIds.indexOf(overId)
      if (oldIndex === -1 || newIndex === -1) return
      if (oldIndex === newIndex) return

      const newCardIds = [...col.cardIds]
      newCardIds.splice(oldIndex, 1)
      newCardIds.splice(newIndex, 0, activeId)

      dispatch({
        type: 'MOVE_CARD',
        cardId: activeId,
        sourceColId: activeColId,
        targetColId: activeColId,
        targetIndex: newIndex,
      })
    } else {
      const targetCol = state.columns.find(c => c.id === targetColId)
      if (!targetCol) return

      const targetIndex = over.data.current?.type === 'column'
        ? targetCol.cardIds.length
        : Math.max(0, targetCol.cardIds.indexOf(overId))

      dispatch({
        type: 'MOVE_CARD',
        cardId: activeId,
        sourceColId: activeColId,
        targetColId,
        targetIndex,
      })
    }
  }

  return (
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 p-6 h-full overflow-x-auto">
          {state.columnOrder.map(colId => {
            const column = state.columns.find(c => c.id === colId)
            if (!column) return null
            return <Column key={column.id} column={column} />
          })}
        </div>
        <DragOverlay>
          {activeCard ? (
            <div className="w-72 opacity-90">
              <KanbanCard card={activeCard} columnId="" />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>
  )
}
