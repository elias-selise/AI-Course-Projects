'use client'

import { useState } from 'react'
import { useBoard } from '../lib/board-context'

interface Props {
  columnId: string
}

export function AddCardForm({ columnId }: Props) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [details, setDetails] = useState('')
  const { dispatch } = useBoard()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    dispatch({ type: 'ADD_CARD', columnId, title: title.trim(), details: details.trim() })
    setTitle('')
    setDetails('')
    setOpen(false)
  }

  function handleCancel() {
    setTitle('')
    setDetails('')
    setOpen(false)
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="w-full py-2 text-xs font-medium text-zinc-400 hover:text-zinc-600 hover:bg-zinc-200/50 rounded-lg transition-colors"
      >
        + Add Card
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-zinc-200 p-3 space-y-2">
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="Card title"
        className="w-full px-2 py-1 text-sm border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        autoFocus
      />
      <textarea
        value={details}
        onChange={e => setDetails(e.target.value)}
        placeholder="Details (optional)"
        className="w-full px-2 py-1 text-xs text-zinc-600 border border-zinc-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        rows={2}
      />
      <div className="flex gap-1">
        <button
          type="submit"
          className="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
        >
          Add
        </button>
        <button
          type="button"
          onClick={handleCancel}
          className="px-2 py-1 text-xs font-medium text-zinc-600 bg-zinc-100 rounded hover:bg-zinc-200"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
