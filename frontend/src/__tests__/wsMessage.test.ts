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

  it('ignores unknown op', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, { op: 'unknown', foo: 'bar' })
    expect(result).toEqual(state)
  })
})
