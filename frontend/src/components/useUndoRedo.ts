import { useState, useCallback } from 'react'

type State<T> = {
  past: T[]
  present: T
  future: T[]
}

export default function useUndoRedo<T>(initial: T, limit = 50) {
  const [history, setHistory] = useState<State<T>>({ past: [], present: initial, future: [] })

  const setState = useCallback((value: T | ((prev: T) => T)) => {
    setHistory(h => {
      const newPresent = typeof value === 'function' ? (value as any)(h.present) : value
      const past = [...h.past, h.present].slice(-limit)
      return { past, present: newPresent, future: [] }
    })
  }, [limit])

  const undo = useCallback(() => {
    setHistory(h => {
      if (!h.past.length) return h
      const previous = h.past[h.past.length - 1]
      const past = h.past.slice(0, -1)
      const future = [h.present, ...h.future]
      return { past, present: previous, future }
    })
  }, [])

  const redo = useCallback(() => {
    setHistory(h => {
      if (!h.future.length) return h
      const next = h.future[0]
      const future = h.future.slice(1)
      const past = [...h.past, h.present].slice(-limit)
      return { past, present: next, future }
    })
  }, [limit])

  return { state: history.present, setState, undo, redo }
}
