import { applyWsMessage, GraphState } from '../wsMessage'
import { describe, it, expect } from 'vitest'

describe('applyWsMessage', () => {
  it('appends a node for create_node', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, { op: 'create_node', node: { id: 1 } })
    expect(result.nodes).toHaveLength(1)
    expect(result.nodes[0]).toEqual({ id: 1 })
  })

  it('ignores unknown op', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, { op: 'unknown', foo: 'bar' })
    expect(result).toEqual(state)
  })

  it('stores numeric ids for create_relation', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, {
      op: 'create_relation',
      id: '2',
      source: '1',
      target: '3',
    })
    expect(typeof result.edges[0].id).toBe('number')
    expect(result.edges[0]).toEqual({ id: 2, source: 1, target: 3 })
  })

  it('keeps numeric ids when provided as numbers', () => {
    const state: GraphState = { nodes: [], edges: [], materials: [] }
    const result = applyWsMessage(state, {
      op: 'create_relation',
      id: 4,
      source: 1,
      target: 2,
    })
    expect(typeof result.edges[0].id).toBe('number')
    expect(result.edges[0]).toEqual({ id: 4, source: 1, target: 2 })
  })
})
