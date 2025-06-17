export interface GraphState {
  nodes: any[]
  edges: any[]
  materials: any[]
}

export interface WsMessage {
  op: string
  [key: string]: any
}

export function applyWsMessage(state: GraphState, msg: WsMessage): GraphState {
  switch (msg.op) {
    case 'create_node':
      if ('node' in msg) {
        return { ...state, nodes: [...state.nodes, msg.node] }
      }
      if ('id' in msg) {
        return { ...state, nodes: [...state.nodes, { id: msg.id }] }
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
