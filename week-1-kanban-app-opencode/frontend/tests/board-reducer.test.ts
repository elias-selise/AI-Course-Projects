import { describe, it, expect } from 'vitest'
import { boardReducer } from '../app/lib/board-reducer'
import { BoardState } from '../app/lib/types'

const initialState: BoardState = {
  columns: [
    { id: 'col1', title: 'Backlog', cardIds: ['c1'] },
    { id: 'col2', title: 'To Do', cardIds: ['c2'] },
  ],
  cards: {
    c1: { id: 'c1', title: 'Task 1', details: 'Details 1' },
    c2: { id: 'c2', title: 'Task 2', details: 'Details 2' },
  },
  columnOrder: ['col1', 'col2'],
}

describe('boardReducer', () => {
  it('adds a card to a column', () => {
    const state = boardReducer(initialState, {
      type: 'ADD_CARD',
      columnId: 'col1',
      title: 'New Task',
      details: 'New details',
    })
    const col = state.columns.find(c => c.id === 'col1')!
    expect(col.cardIds).toHaveLength(2)
    const newCardId = col.cardIds[1]
    expect(state.cards[newCardId].title).toBe('New Task')
    expect(state.cards[newCardId].details).toBe('New details')
  })

  it('deletes a card from all columns', () => {
    const state = boardReducer(initialState, {
      type: 'DELETE_CARD',
      cardId: 'c1',
    })
    expect(state.cards['c1']).toBeUndefined()
    expect(state.columns.find(c => c.id === 'col1')!.cardIds).not.toContain('c1')
  })

  it('moves a card between columns', () => {
    const state = boardReducer(initialState, {
      type: 'MOVE_CARD',
      cardId: 'c1',
      sourceColId: 'col1',
      targetColId: 'col2',
      targetIndex: 1,
    })
    expect(state.columns.find(c => c.id === 'col1')!.cardIds).toEqual([])
    expect(state.columns.find(c => c.id === 'col2')!.cardIds).toEqual(['c2', 'c1'])
  })

  it('moves a card within the same column', () => {
    const state = boardReducer(
      { ...initialState, columns: [{ id: 'col1', title: 'B', cardIds: ['c1', 'c2'] }] },
      {
        type: 'MOVE_CARD',
        cardId: 'c2',
        sourceColId: 'col1',
        targetColId: 'col1',
        targetIndex: 0,
      }
    )
    expect(state.columns.find(c => c.id === 'col1')!.cardIds).toEqual(['c2', 'c1'])
  })

  it('renames a column', () => {
    const state = boardReducer(initialState, {
      type: 'RENAME_COLUMN',
      columnId: 'col1',
      title: 'New Name',
    })
    expect(state.columns.find(c => c.id === 'col1')!.title).toBe('New Name')
  })

  it('edits a card', () => {
    const state = boardReducer(initialState, {
      type: 'EDIT_CARD',
      cardId: 'c1',
      title: 'Updated',
      details: 'Updated details',
    })
    expect(state.cards['c1'].title).toBe('Updated')
    expect(state.cards['c1'].details).toBe('Updated details')
  })
})
