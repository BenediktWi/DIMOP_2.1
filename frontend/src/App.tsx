import React, { useEffect, useState, useRef } from 'react'
import GraphCanvas from './components/GraphCanvas'
import ComponentTable from './components/ComponentTable'
import useUndoRedo from './components/useUndoRedo'
import { applyWsMessage, GraphState, WsMessage, Component } from './wsMessage'

export default function App() {
  // local state & undo/redo stack
  const { state, setState, undo, redo } = useUndoRedo<GraphState>({ nodes: [], edges: [], materials: [] }, 50)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [showNodeForm, setShowNodeForm] = useState(false)
  const [newNode, setNewNode] = useState({
    name: '',
    level: 0,
    parent_id: '',
    atomic: false,
    weight: 1,
    reusable: false,
    recyclable: false,
    connection_type: 0,
    material_id: '' as string | number,
  })
  const [availableNodes, setAvailableNodes] = useState<Component[]>([])
  const [availableLevels, setAvailableLevels] = useState<number[]>([])

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
      .then((data) => {
        setState({
          ...data,
          nodes: data.nodes.map((n: any) => ({
            ...n,
            position: { x: Math.random() * 250, y: Math.random() * 250 },
          })),
        })
        if (!data.materials.length) {
          addMaterial()
        }
      })
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

  const addMaterial = () => {
    const name = window.prompt('Name of material', '')
    if (!name) return
    const weight = parseFloat(window.prompt('Weight of material', '1') || '1')
    const co2 = parseFloat(window.prompt('CO2 value', '1') || '1')
    const hardnessStr = window.prompt('Hardness value', '1') || '1'
    const hardness = parseFloat(hardnessStr)
    if (Number.isNaN(hardness)) {
      window.alert('Hardness must be a number')
      return
    }
    fetch('/materials/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, weight, co2_value: co2, hardness }),
    })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(material =>
        setState(prev =>
          applyWsMessage(prev, {
            op: 'create_material',
            material,
          })
        )
      )
      .catch(err => console.error(err))
  }

  const addNode = () => {
    setShowNodeForm(true)
  }

  useEffect(() => {
    if (!showNodeForm) return
    fetch(`/projects/${projectId}/graph`)
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(data => {
        setAvailableNodes(data.nodes)
        const max = Math.max(0, ...data.nodes.map((n: any) => n.level ?? 0))
        const lvls = Array.from({ length: max + 2 }, (_, i) => i)
        setAvailableLevels(lvls)
      })
      .catch(err => console.error(err))
  }, [showNodeForm, projectId])

  const handleNodeSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (newNode.material_id === '') {
      window.alert('Please select a material')
      return
    }
    const payload: any = {
      project_id: Number(projectId),
      name: newNode.name,
      level: Number(newNode.level),
      parent_id: newNode.parent_id === '' ? null : Number(newNode.parent_id),
      atomic: newNode.atomic,
      reusable: newNode.reusable,
      recyclable: newNode.recyclable,
      connection_type: newNode.connection_type,
      material_id: Number(newNode.material_id),
    }
    if (newNode.atomic) {
      payload.weight = Number(newNode.weight)
    }
    fetch('/nodes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
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
      .finally(() => {
        setShowNodeForm(false)
        setNewNode({
          name: '',
          level: 0,
          parent_id: '',
          atomic: false,
          weight: 1,
          reusable: false,
          recyclable: false,
          connection_type: 0,
          material_id: '',
        })
        setAvailableNodes([])
        setAvailableLevels([])
      })
  }

  const handleParentChange = (pid: string) => {
    if (pid === '') {
      setNewNode(prev => ({ ...prev, parent_id: '', level: 0 }))
      return
    }
    const parent = availableNodes.find(n => String(n.id) === pid)
    const lvl = parent ? (parent.level ?? 0) + 1 : 1
    setNewNode(prev => ({ ...prev, parent_id: pid, level: lvl }))
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
        {showNodeForm && (
          <form className="p-2 space-y-2" onSubmit={handleNodeSubmit}>
            <input
              placeholder="Name"
              value={newNode.name}
              onChange={e => setNewNode({ ...newNode, name: e.target.value })}
            />
            <select
              value={newNode.level}
              disabled={newNode.parent_id !== ''}
              onChange={e => {
                const lvl = Number(e.target.value)
                setNewNode(prev => ({
                  ...prev,
                  level: lvl,
                  parent_id: lvl === 0 ? '' : prev.parent_id,
                }))
              }}
            >
              {availableLevels.map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
            <select
              value={newNode.parent_id}
              disabled={newNode.level === 0}
              onChange={e => handleParentChange(e.target.value)}
            >
              <option value="">Select parent</option>
              {availableNodes.map(n => (
                <option key={n.id} value={n.id}>{n.id}{n.name ? ` - ${n.name}` : ''}</option>
              ))}
            </select>
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.atomic}
                onChange={e => setNewNode({ ...newNode, atomic: e.target.checked })}
              />
              Atomic
            </label>
            <input
              type="number"
              step="any"
              placeholder="Weight"
              value={newNode.weight}
              disabled={!newNode.atomic}
              onChange={e => setNewNode({ ...newNode, weight: Number(e.target.value) })}
            />
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.reusable}
                onChange={e => setNewNode({ ...newNode, reusable: e.target.checked })}
              />
              Reusable
            </label>
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.recyclable}
                onChange={e => setNewNode({ ...newNode, recyclable: e.target.checked })}
              />
              Recyclable
            </label>
            <select
              value={newNode.connection_type}
              onChange={e =>
                setNewNode({ ...newNode, connection_type: Number(e.target.value) })
              }
            >
              {[0, 1, 2, 3, 4, 5].map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
            <select
              value={newNode.material_id}
              onChange={e => setNewNode({ ...newNode, material_id: e.target.value })}
            >
              <option value="">Select material</option>
              {state.materials.map(m => (
                <option key={m.id} value={m.id}>{m.id}{m.name ? ` - ${m.name}` : ''}</option>
              ))}
            </select>
            <div className="space-x-2">
              <button type="submit">Create</button>
              <button type="button" onClick={() => setShowNodeForm(false)}>Cancel</button>
            </div>
          </form>
        )}
        <div className="p-2 space-x-2">
          <button onClick={addNode}>Add Node</button>
          <button onClick={addMaterial}>Add Material</button>
          <button onClick={undo}>Undo</button>
          <button onClick={redo}>Redo</button>
        </div>
      </div>
      <div className="w-1/3 h-full">
        <ComponentTable components={state.nodes} />
      </div>
    </div>
  )
}