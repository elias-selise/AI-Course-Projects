export interface Card {
  id: string
  title: string
  details: string
}

export interface Column {
  id: string
  title: string
  cardIds: string[]
}

export interface BoardState {
  columns: Column[]
  cards: Record<string, Card>
  columnOrder: string[]
}

export type BoardAction =
  | { type: 'ADD_CARD'; columnId: string; title: string; details: string }
  | { type: 'DELETE_CARD'; cardId: string }
  | { type: 'MOVE_CARD'; cardId: string; sourceColId: string; targetColId: string; targetIndex: number }
  | { type: 'RENAME_COLUMN'; columnId: string; title: string }
  | { type: 'EDIT_CARD'; cardId: string; title: string; details: string }
