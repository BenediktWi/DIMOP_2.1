export interface Component {
  id: number
  name?: string
  level?: number
  parent_id?: number | null
  atomic?: boolean
  weight?: number
  reusable?: boolean
  connection_type?: string | number
  material_id?: number
  sustainability_score?: number
  position?: { x: number; y: number }
}

export interface Material {
  id: number
  name?: string
  weight?: number
  co2_value?: number
  hardness?: number
}

export interface Edge {
  id: number
  source: number
  target: number
}

export interface GraphState {
  nodes: Component[]
  edges: Edge[]
  materials: Material[]
}

export interface WsMessage {
  op: string
  [key: string]: any
}

export function applyWsMessage(state: GraphState, msg: WsMessage): GraphState {
  switch (msg.op) {
    case 'create_node':
      if ('node' in msg) {
        const n = {
          ...msg.node,
          position: msg.node.position ?? {
            x: Math.random() * 250,
            y: Math.random() * 250,
          },
        }
        if (n.atomic === false) {
          delete (n as any).weight
        }
        return { ...state, nodes: [...state.nodes, n] }
      }
      if ('id' in msg) {
        return {
          ...state,
          nodes: [
            ...state.nodes,
            { id: msg.id, position: { x: Math.random() * 250, y: Math.random() * 250 } },
          ],
        }
      }
      return state
    case 'delete_node':
      if ('id' in msg) {
        return { ...state, nodes: state.nodes.filter(n => n.id !== msg.id) }
      }
      return state
      case 'create_relation':
        if ('id' in msg && 'source' in msg && 'target' in msg) {
          return {
            ...state,
            edges: [
              ...state.edges,
              {
                id: Number(msg.id),
                source: Number(msg.source),
                target: Number(msg.target),
              },
            ],
          }
        }
      return state
    case 'delete_relation':
      if ('id' in msg) {
        const id = Number(msg.id)
        return { ...state, edges: state.edges.filter(e => e.id !== id) }
      }
      return state
    case 'create_material':
      if ('material' in msg) {
        return { ...state, materials: [...state.materials, msg.material] }
      }
      if ('id' in msg) {
        return { ...state, materials: [...state.materials, { id: msg.id }] }
      }
      return state
    case 'delete_material':
      if ('id' in msg) {
        return { ...state, materials: state.materials.filter(m => m.id !== msg.id) }
      }
      return state
    default:
      return state
  }
}
