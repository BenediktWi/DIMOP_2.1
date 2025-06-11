import React, { useEffect, useState, useRef } from 'react'
import GraphCanvas from './components/GraphCanvas'
import MaterialTable from './components/MaterialTable'
import useUndoRedo from './components/useUndoRedo'
import { applyWsMessage, GraphState, WsMessage } from './wsMessage'

export default function App() {
  // local state & undo/redo stack
  const { state, setState, undo, redo } = useUndoRedo<GraphState>({ nodes: [], edges: [], materials: [] }, 50)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  // pick up ?project= query param once and remember in localStorage
  const [projectId] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    const query = params.get('project')
    if (query) {
      localStorage.setItem('projectId', query)
      return query
    }
    return localStorage.getItem('projectId') ?? '1'
  })

  /**
   * 1️⃣  Initial data fetch (REST)
   * Fetches the current graph state once when the component mounts or when the
   * project id changes. The result seeds the undo‑stack and UI.
   */
  useEffect(() => {
    fetch(`/projects/${projectId}/graph`)
      .then((r) => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}`)
        }
        return r.json()
      })
      .then((data) =>
        setState({
          ...data,
          nodes: data.nodes.map((n: any) => ({
            ...n,
            position: { x: Math.random() * 250, y: Math.random() * 250 },
          })),
        })
      )
      .catch(() => setError('Failed to load project data'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  /**
   * 2️⃣  Live updates via WebSocket
   * Creates exactly one socket connection per tab & project. Closes it again
   * when the component unmounts.
   */
  useEffect(() => {
    if (wsRef.current) return // already connected

    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = import.meta.env.VITE_WS_HOST ?? 'localhost:8000'
    const wsUrl = `${scheme}://${host}/socket/projects/${projectId}`
    console.log(`Attempting to connect WebSocket to: ${wsUrl}`)

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onmessage = (ev) => {
      try {
        const msg: WsMessage = JSON.parse(ev.data)
        setState((prev) => applyWsMessage(prev, msg))
      } catch {
        console.error('Invalid WS message', ev.data)
      }
    }

    // tidy up on unmount or before refresh
    const handleClose = () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    }

    window.addEventListener('beforeunload', handleClose)

    return () => {
      window.removeEventListener('beforeunload', handleClose)
      handleClose()
      wsRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setState, projectId])

  if (error) {
    return <div className="p-4 text-red-600">{error}</div>
  }

  const addNode = () => {
    if (!state.materials.length) return
    fetch('/nodes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: Number(projectId),
        material_id: state.materials[0].id,
        level: 0,
      }),
    })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(node =>
        setState(prev =>
          applyWsMessage(prev, {
            op: 'create_node',
            node,
          })
        )
      )
      .catch(err => console.error(err))
  }

  const handleConnect = (connection: any) => {
    if (!connection.source || !connection.target) return
    fetch('/relations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: Number(projectId),
        source_id: Number(connection.source),
        target_id: Number(connection.target),
      }),
    }).catch((err) => console.error(err))
  }

  return (
    <div className="flex h-full w-full">
      <div className="w-2/3 h-full">
        <GraphCanvas nodes={state.nodes} edges={state.edges} onConnectEdge={handleConnect} />
        <div className="p-2 space-x-2">
          <button onClick={addNode}>Add Node</button>
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