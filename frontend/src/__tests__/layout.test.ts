import { describe, it, expect } from 'vitest'
import { layoutNodesByLevel, X_OFFSET, Y_SPACING } from '../components/GraphCanvas'

describe('layoutNodesByLevel', () => {
  it('positions nodes according to level and index', () => {
    const nodes = [
      { id: 1, level: 0 },
      { id: 2, level: 0 },
      { id: 3, level: 1 },
      { id: 4, level: 2 },
    ]
    const result = layoutNodesByLevel(nodes)
    expect(result[0].position).toEqual({ x: 0 * X_OFFSET, y: 0 * Y_SPACING })
    expect(result[1].position).toEqual({ x: 0 * X_OFFSET, y: 1 * Y_SPACING })
    expect(result[2].position).toEqual({ x: 1 * X_OFFSET, y: 0 * Y_SPACING })
    expect(result[3].position).toEqual({ x: 2 * X_OFFSET, y: 0 * Y_SPACING })
  })
})
