import { BoardState, BoardAction, Card } from './types'

let nextId = 100

function generateId(): string {
  return `c${nextId++}`
}

export function boardReducer(state: BoardState, action: BoardAction): BoardState {
  switch (action.type) {
    case 'ADD_CARD': {
      const id = generateId()
      const card = { id, title: action.title, details: action.details }
      return {
        ...state,
        cards: { ...state.cards, [id]: card },
        columns: state.columns.map(col =>
          col.id === action.columnId
            ? { ...col, cardIds: [...col.cardIds, id] }
            : col
        ),
      }
    }
    case 'DELETE_CARD': {
      const remainingCards: Record<string, Card> = {}
      for (const [id, card] of Object.entries(state.cards)) {
        if (id !== action.cardId) remainingCards[id] = card
      }
      return {
        ...state,
        cards: remainingCards,
        columns: state.columns.map(col => ({
          ...col,
          cardIds: col.cardIds.filter(id => id !== action.cardId),
        })),
      }
    }
    case 'MOVE_CARD': {
      const sourceCol = state.columns.find(c => c.id === action.sourceColId)
      const targetCol = state.columns.find(c => c.id === action.targetColId)
      if (!sourceCol || !targetCol) return state

      const sourceCardIds = sourceCol.cardIds.filter(id => id !== action.cardId)
      const targetCardIds = targetCol.id === action.sourceColId
        ? sourceCardIds
        : [...targetCol.cardIds]

      targetCardIds.splice(action.targetIndex, 0, action.cardId)

      return {
        ...state,
        columns: state.columns.map(col => {
          if (col.id === action.sourceColId) return { ...col, cardIds: sourceCardIds }
          if (col.id === action.targetColId) return { ...col, cardIds: targetCardIds }
          return col
        }),
      }
    }
    case 'RENAME_COLUMN': {
      return {
        ...state,
        columns: state.columns.map(col =>
          col.id === action.columnId ? { ...col, title: action.title } : col
        ),
      }
    }
    case 'EDIT_CARD': {
      return {
        ...state,
        cards: {
          ...state.cards,
          [action.cardId]: {
            ...state.cards[action.cardId],
            title: action.title,
            details: action.details,
          },
        },
      }
    }
    default:
      return state
  }
}
