import React from 'react'
import ReactFlow, { MiniMap, Controls, Background, Connection } from 'reactflow'
import 'reactflow/dist/style.css'

/** Fixed spacing for node layout */
export const X_OFFSET = 250
export const Y_SPACING = 100

export function layoutNodesByLevel(nodes: any[]) {
  const counts: Record<number, number> = {}
  return nodes.map(n => {
    const level = n.level ?? 0
    const yIndex = counts[level] ?? 0
    counts[level] = yIndex + 1
    return {
      ...n,
      position: { x: level * X_OFFSET, y: yIndex * Y_SPACING },
    }
  })
}

function adaptNodes(nodes: any[]) {
  return layoutNodesByLevel(nodes).map(n => ({
    ...n,
    id: String(n.id),
    data: { label: n.name ?? String(n.id) },
  }))
}

function adaptEdges(edges: any[]) {
  return edges.map(e => ({
    ...e,
    id: String(e.id),
    source: String(e.source),
    target: String(e.target),
  }))
}


interface Props {
  nodes: any[]
  edges: any[]
  onConnectEdge: (connection: Connection) => void
}

export default function GraphCanvas({ nodes, edges, onConnectEdge }: Props) {
  const laidOut = adaptNodes(nodes)
  const adaptedEdges = adaptEdges(edges)
  const maxLevel = Math.max(0, ...nodes.map(n => n.level ?? 0))

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {Array.from({ length: maxLevel + 1 }).map((_, lvl) => (
        <div
          key={lvl}
          style={{
            position: 'absolute',
            left: lvl * X_OFFSET,
            top: 0,
            bottom: 0,
            width: X_OFFSET,
            borderRight: '1px solid #eee',
            pointerEvents: 'none',
          }}
        />
      ))}
      <ReactFlow
        nodes={laidOut}
        edges={adaptedEdges}
        onConnect={onConnectEdge}
        fitView
        style={{ width: '100%', height: '100%' }}
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  )
}
