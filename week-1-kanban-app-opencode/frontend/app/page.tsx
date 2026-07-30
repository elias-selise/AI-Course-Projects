'use client'

import dynamic from 'next/dynamic'
import { BoardProvider } from './lib/board-context'

const Board = dynamic(() => import('./components/Board').then(m => m.Board), { ssr: false })

export default function Home() {
  return (
    <BoardProvider>
      <div className="flex flex-col h-screen bg-zinc-100">
        <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-zinc-200">
          <h1 className="text-lg font-bold text-zinc-800">Kanban Board</h1>
        </header>
        <main className="flex-1 overflow-hidden">
          <Board />
        </main>
      </div>
    </BoardProvider>
  )
}
