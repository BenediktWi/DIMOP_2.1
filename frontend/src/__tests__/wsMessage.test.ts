import { applyWsMessage, GraphState } from '../wsMessage'
import { describe, it, expect } from 'vitest'

/**
 * Unit‑tests for the reducer/patcher that applies server‑sent WebSocket
 * messages to the local GraphState. Covers all currently supported operations
 * with a tiny, in‑memory state so the tests stay lightning‑fast.
 */

describe('applyWsMessage', () => {
  it('appends a node for create_node', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }

    const result = applyWsMessage(state, {
      op: 'create_node',
      node: { id: 1 },
    })

    expect(result.nodes).toHaveLength(1)
    expect(result.nodes[0]).toHaveProperty('id', 1)
    // the reducer should always attach a position so the UI can render the node
    expect(result.nodes[0]).toHaveProperty('position')
  })

  it('preserves component fields on create_node', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }

    const result = applyWsMessage(state, {
      op: 'create_node',
      node: {
        id: 2,
        name: 'Comp',
        level: 1,
        parent_id: null,
        atomic: true,
        weight: 3,
        reusable: false,
        connection_type: 'GLUE',
        material_id: 5,
      },
    })

    const n = result.nodes[0]
    expect(n.name).toBe('Comp')
    expect(n.level).toBe(1)
    expect(n.atomic).toBe(true)
    expect(n.weight).toBe(3)
    expect(n.connection_type).toBe('GLUE')
  })

  it('omits weight for non‑atomic node', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }

    const result = applyWsMessage(state, {
      op: 'create_node',
      node: {
        id: 3,
        name: 'Group',
        level: 0,
        parent_id: null,
        atomic: false,
        reusable: false,
        connection_type: 'BOLT', // ✅ canonical upper‑case enum value
      },
    })

    const n = result.nodes[0]
    expect(n.atomic).toBe(false)
    expect(n.weight).toBeUndefined()
  })

  it('ignores unknown op', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }

    const result = applyWsMessage(state, { op: 'unknown', foo: 'bar' } as any)
    expect(result).toEqual(state)
  })
})
