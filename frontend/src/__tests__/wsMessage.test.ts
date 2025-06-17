import { applyWsMessage, GraphState } from '../wsMessage'
import { describe, it, expect } from 'vitest'

describe('applyWsMessage', () => {
  it('appends a node for create_node', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, { op: 'create_node', node: { id: 1 } })
    expect(result.nodes).toHaveLength(1)
    expect(result.nodes[0]).toHaveProperty('id', 1)
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
        connection_type: 2,
        material_id: 5,
      },
    })
    const n = result.nodes[0]
    expect(n.name).toBe('Comp')
    expect(n.level).toBe(1)
    expect(n.atomic).toBe(true)
    expect(n.weight).toBe(3)
    expect(n.connection_type).toBe(2)
  })

  it('omits weight for non atomic node', () => {
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
        connection_type: 'bolt',
      },
    })
    const n = result.nodes[0]
    expect(n.atomic).toBe(false)
    expect(n.weight).toBeUndefined()
  })

  it('ignores unknown op', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, { op: 'unknown', foo: 'bar' })
    expect(result).toEqual(state)
  })
})
