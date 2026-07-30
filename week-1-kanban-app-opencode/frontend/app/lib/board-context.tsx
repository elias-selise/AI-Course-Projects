'use client'

import { createContext, useContext, useReducer, ReactNode } from 'react'
import { BoardState, BoardAction } from './types'
import { initialBoardState } from './data'
import { boardReducer } from './board-reducer'

const BoardContext = createContext<{
  state: BoardState
  dispatch: React.Dispatch<BoardAction>
} | null>(null)

export function BoardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(boardReducer, initialBoardState)
  return (
    <BoardContext.Provider value={{ state, dispatch }}>
      {children}
    </BoardContext.Provider>
  )
}

export function useBoard() {
  const ctx = useContext(BoardContext)
  if (!ctx) throw new Error('useBoard must be used within BoardProvider')
  return ctx
}
