import { Component } from './wsMessage'

export default function filterParentCandidates(nodes: Component[], level: number): Component[] {
  return nodes.filter(n => (n.level ?? 0) === level - 1)
}
