import React, { useEffect, useState, useRef } from 'react'
import GraphCanvas, { layoutNodesByLevel } from './components/GraphCanvas'
import ComponentTable from './components/ComponentTable'
import MaterialTable from './components/MaterialTable'
import useUndoRedo from './components/useUndoRedo'
import { applyWsMessage, GraphState, WsMessage, Component } from './wsMessage'

/**
 * 🔧 Keep a single source‑of‑truth for the allowed connection types so we can
 * validate user input and avoid magic strings throughout the codebase.
 */
export enum ConnectionType {
  SCREW = 'SCREW',
  BOLT = 'BOLT',
  GLUE = 'GLUE',
  WELD = 'WELD',
  NAIL = 'NAIL',
  CLIP = 'CLIP',
}
const CONNECTION_TYPES = Object.values(ConnectionType) as ConnectionType[]

/**
 * Shape of the temporary form state when a user creates a new node.
 */
type NewNodeState = {
  name: string
  level: number
  parent_id: string
  atomic: boolean
  weight: number
  reusable: boolean
  recyclable: boolean
  connection_type: ConnectionType
  material_id: string // empty string = “nothing selected yet”
}

const DEFAULT_NEW_NODE: NewNodeState = {
  name: '',
  level: 0,
  parent_id: '',
  atomic: false,
  weight: 1,
  reusable: false,
  recyclable: false,
  connection_type: ConnectionType.SCREW,
  material_id: '',
}

export default function App() {
  /* --------------------------------------------------------------------- */
  /*  1️⃣  Local state & undo/redo stack                                   */
  /* --------------------------------------------------------------------- */
  const { state, setState, undo, redo } = useUndoRedo<GraphState>(
    { nodes: [], edges: [], materials: [] },
    50,
  )
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [showNodeForm, setShowNodeForm] = useState(false)
  const [newNode, setNewNode] = useState<NewNodeState>(DEFAULT_NEW_NODE)
  const [availableNodes, setAvailableNodes] = useState<Component[]>([])
  const [availableLevels, setAvailableLevels] = useState<number[]>([])

  /* --------------------------------------------------------------------- */
  /*  Handy helper: keep ?project= URL param in localStorage               */
  /* --------------------------------------------------------------------- */
  const [projectId] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    const query = params.get('project')
    if (query) {
      localStorage.setItem('projectId', query)
      return query
    }
    return localStorage.getItem('projectId') ?? '1'
  })

  /* --------------------------------------------------------------------- */
  /*  2️⃣  Initial data fetch (REST)                                        */
  /* --------------------------------------------------------------------- */
  useEffect(() => {
    let isMounted = true

    fetch(`/projects/${projectId}/graph`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => {
        if (!isMounted) return
        setState({
          ...data,
          nodes: layoutNodesByLevel(data.nodes),
        })

        // ensure there is at least one material so the “add node” form works
        if (isMounted && !data.materials.length) addMaterial()
      })
      .catch(() => isMounted && setError('Failed to load project data'))

    return () => {
      isMounted = false
    }
    // deliberately omit setState from deps – useUndoRedo gives us a stable ref
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  /* --------------------------------------------------------------------- */
  /*  3️⃣  Live updates via WebSocket                                       */
  /* --------------------------------------------------------------------- */
  useEffect(() => {
    if (wsRef.current) return // already connected in this tab

    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = import.meta.env.VITE_WS_HOST ?? 'localhost:8000'
    const wsUrl = `${scheme}://${host}/socket/projects/${projectId}`
    console.log(`Connecting WebSocket to: ${wsUrl}`)

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

    // tidy up when the component unmounts or the tab is refreshed
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

  /* --------------------------------------------------------------------- */
  /*  4️⃣  Populate selectors when the “create node” form opens             */
  /* --------------------------------------------------------------------- */
  useEffect(() => {
    if (!showNodeForm) return

    fetch(`/projects/${projectId}/graph`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => {
        setAvailableNodes(data.nodes)
        const max = Math.max(0, ...data.nodes.map((n: any) => n.level ?? 0))
        setAvailableLevels(Array.from({ length: max + 2 }, (_, i) => i))
      })
      .catch((err) => console.error(err))
  }, [showNodeForm, projectId])

  /* --------------------------------------------------------------------- */
  /*  5️⃣  High‑level render guards                                         */
  /* --------------------------------------------------------------------- */
  if (error) {
    return <div className="p-4 text-red-600">{error}</div>
  }

  /* --------------------------------------------------------------------- */
  /*  6️⃣  Helper functions                                                 */
  /* --------------------------------------------------------------------- */
  const addMaterial = () => {
    const name = window.prompt('Name of material', '')?.trim()
    if (!name) return

    const weight = parseFloat(window.prompt('Weight of material', '1') ?? '1')
    const co2 = parseFloat(window.prompt('CO2 value', '1') ?? '1')
    const hardnessStr = window.prompt('Hardness value', '1') ?? '1'
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
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((material) =>
        setState((prev) =>
          applyWsMessage(prev, {
            op: 'create_material',
            material,
          }),
        ),
      )
      .catch((err) => console.error(err))
  }

  const addNode = () => setShowNodeForm(true)

  /* --------------------------------------------------------------------- */
  /*  7️⃣  Handle node creation                                             */
  /* --------------------------------------------------------------------- */
  const handleNodeSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!newNode.material_id) {
      window.alert('Please select a material')
      return
    }

    const payload: Record<string, unknown> = {
      project_id: Number(projectId),
      name: newNode.name.trim(),
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

    try {
      const response = await fetch('/nodes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 404) {
          setError('Node creation failed: referenced item not found. Check your selections.')
          return
        }
        setError(`Failed to create node (HTTP ${response.status})`)
        return
      }

      const node = await response.json()
      setState((prev) => applyWsMessage(prev, { op: 'create_node', node }))
    } catch (err) {
      console.error(err)
      setError('Failed to create node')
    } finally {
      // always close the form & reset state
      setShowNodeForm(false)
      setNewNode(DEFAULT_NEW_NODE)
      // clear cached selectors so they refresh next time
      setAvailableNodes([])
      setAvailableLevels([])
    }
  }

  /* --------------------------------------------------------------------- */
  /*  8️⃣  Misc. handlers                                                   */
  /* --------------------------------------------------------------------- */
  const handleParentChange = (pid: string) => {
    if (pid === '') {
      setNewNode((prev) => ({ ...prev, parent_id: '', level: 0 }))
      return
    }
    const parent = availableNodes.find((n) => String(n.id) === pid)
    const lvl = parent ? (parent.level ?? 0) + 1 : 1
    setNewNode((prev) => ({ ...prev, parent_id: pid, level: lvl }))
  }

  const handleConnect = (connection: { source?: string; target?: string }) => {
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

  const deleteNode = (id: number) => {
    fetch(`/nodes/${id}`, { method: 'DELETE' }).catch(err => console.error(err))
  }

  const deleteMaterial = (id: number) => {
    fetch(`/materials/${id}`, { method: 'DELETE' }).catch(err => console.error(err))
  }

  /* --------------------------------------------------------------------- */
  /*  9️⃣  Render                                                           */
  /* --------------------------------------------------------------------- */
  return (
    <div className="flex h-full w-full">
      {/* ----------------------------------------------------------------- */}
      <div className="w-2/3 h-full">
        <GraphCanvas nodes={state.nodes} edges={state.edges} onConnectEdge={handleConnect} />

        {/* ----------------------- Create node overlay -------------------- */}
        {showNodeForm && (
          <form className="p-2 space-y-2" onSubmit={handleNodeSubmit}>
            <input
              className="block w-full border p-1"
              placeholder="Name"
              value={newNode.name}
              onChange={(e) => setNewNode({ ...newNode, name: e.target.value })}
            />

            {/* Level selector */}
            <select
              className="border p-1"
              value={newNode.level}
              disabled={newNode.parent_id !== ''}
              onChange={(e) => {
                const lvl = Number(e.target.value)
                setNewNode((prev) => ({
                  ...prev,
                  level: lvl,
                  parent_id: lvl === 0 ? '' : prev.parent_id,
                }))
              }}
            >
              {availableLevels.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>

            {/* Parent selector */}
            <select
              className="border p-1"
              value={newNode.parent_id}
              disabled={newNode.level === 0}
              onChange={(e) => handleParentChange(e.target.value)}
            >
              <option value="">Select parent</option>
              {availableNodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.id}
                  {n.name ? ` - ${n.name}` : ''}
                </option>
              ))}
            </select>

            {/* Atomic + weight */}
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.atomic}
                onChange={(e) => setNewNode({ ...newNode, atomic: e.target.checked })}
              />
              {' '}Atomic
            </label>
            <input
              className="border p-1"
              type="number"
              step="any"
              placeholder="Weight"
              value={newNode.weight}
              disabled={!newNode.atomic}
              onChange={(e) => setNewNode({ ...newNode, weight: Number(e.target.value) })}
            />

            {/* Reusable / recyclable */}
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.reusable}
                onChange={(e) => setNewNode({ ...newNode, reusable: e.target.checked })}
              />
              {' '}Reusable
            </label>
            <label className="block">
              <input
                type="checkbox"
                checked={newNode.recyclable}
                onChange={(e) => setNewNode({ ...newNode, recyclable: e.target.checked })}
              />
              {' '}Recyclable
            </label>

            {/* Connection type */}
            <select
              className="border p-1"
              value={newNode.connection_type}
              onChange={(e) =>
                setNewNode({ ...newNode, connection_type: e.target.value as ConnectionType })
              }
            >
              {CONNECTION_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>

            {/* Material selector */}
            <select
              className="border p-1"
              value={newNode.material_id}
              onChange={(e) => setNewNode({ ...newNode, material_id: e.target.value })}
            >
              <option value="">Select material</option>
              {state.materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.id}
                  {m.name ? ` - ${m.name}` : ''}
                </option>
              ))}
            </select>

            {/* Form actions */}
            <div className="space-x-2">
              <button type="submit" className="border px-2 py-1">
                Create
              </button>
              <button
                type="button"
                className="border px-2 py-1"
                onClick={() => setShowNodeForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Main toolbar */}
        <div className="p-2 space-x-2">
          <button className="border px-2 py-1" onClick={addNode}>
            Add Node
          </button>
          <button className="border px-2 py-1" onClick={addMaterial}>
            Add Material
          </button>
          <button className="border px-2 py-1" onClick={undo}>
            Undo
          </button>
          <button className="border px-2 py-1" onClick={redo}>
            Redo
          </button>
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      <div className="w-1/3 h-full overflow-auto border-l">
        <ComponentTable components={state.nodes} onDelete={deleteNode} />
        <MaterialTable materials={state.materials} onDelete={deleteMaterial} />
      </div>
    </div>
  )
}
