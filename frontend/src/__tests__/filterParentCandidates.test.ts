import { describe, it, expect } from 'vitest'
import filterParentCandidates from '../filterParentCandidates'
import type { Component } from '../wsMessage'

describe('filterParentCandidates', () => {
  it('returns nodes whose level equals level - 1', () => {
    const nodes: Component[] = [
      { id: 1, level: 0 },
      { id: 2, level: 1 },
      { id: 3, level: 2 },
    ]
    expect(filterParentCandidates(nodes, 2)).toEqual([{ id: 2, level: 1 }])
  })

  it('handles missing level as 0', () => {
    const nodes: Component[] = [{ id: 1 }, { id: 2, level: 1 }]
    expect(filterParentCandidates(nodes, 1)).toEqual([{ id: 1 }])
  })
})
