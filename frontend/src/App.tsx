import React, { useEffect, useState } from 'react'
import GraphCanvas from './components/GraphCanvas'
import MaterialTable from './components/MaterialTable'
import useUndoRedo from './components/useUndoRedo'
import { applyWsMessage, GraphState, WsMessage } from './wsMessage'

export default function App() {
  const { state, setState, undo, redo } = useUndoRedo<GraphState>({ nodes: [], edges: [], materials: [] }, 50)
  const [error, setError] = useState<string | null>(null)

  const [projectId] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    const query = params.get('project')
    if (query) {
      localStorage.setItem('projectId', query)
      return query
    }
    return localStorage.getItem('projectId') ?? '1'
  })

  useEffect(() => {
    fetch(`/projects/${projectId}/graph`)
      .then(r => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}`)
        }
        return r.json()
      })
      .then(setState)
      .catch(() => setError('Failed to load project data'))
  }, [projectId])

  useEffect(() => {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${scheme}://${window.location.host}/ws/projects/${projectId}`)
    ws.onmessage = ev => {
      try {
        const msg: WsMessage = JSON.parse(ev.data)
        setState(prev => applyWsMessage(prev, msg))
      } catch {
        console.error('Invalid WS message', ev.data)
      }
    }
    return () => ws.close()
  }, [setState, projectId])

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
