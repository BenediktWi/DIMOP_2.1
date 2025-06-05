import React, { useEffect, useState } from 'react'
import GraphCanvas from './components/GraphCanvas'
import MaterialTable from './components/MaterialTable'
import useUndoRedo from './components/useUndoRedo'

export default function App() {
  const [data, setData] = useState({ nodes: [], edges: [], materials: [] })
  const { state, setState, undo, redo } = useUndoRedo(data, 50)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/projects/1/graph')
      .then(r => {
        if (!r.ok) throw new Error(r.statusText)
        return r.json()
      })
      .then(setState)
      .catch(err => console.error('Failed to load project', err))
  }, [])

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.host}/ws/projects/1`)
    ws.onmessage = ev => {
      const patch = JSON.parse(ev.data)
      setState(prev => ({ ...prev, ...patch }))
    }
    return () => ws.close()
  }, [setState])

  if (error) {
    return <div className="p-4 text-red-600">{error}</div>
  }

  return (
    <div className="flex h-full">
      <div className="w-2/3 h-full">
        <GraphCanvas nodes={state.nodes} edges={state.edges} onChange={setState} />
        <div className="p-2 space-x-2">
          <button onClick={undo}>Undo</button>
          <button onClick={redo}>Redo</button>
        </div>
      </div>
      <div className="w-1/3 h-full">
        <MaterialTable materials={state.materials} onDelete={() => {}} />
      </div>
    </div>
  )
}
