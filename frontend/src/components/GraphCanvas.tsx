import React from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  Connection,
  Node as RFNode,
  Edge as RFEdge,
} from 'reactflow'
import 'reactflow/dist/style.css'


interface Props {
  nodes: any[]
  edges: any[]
  onConnectEdge: (connection: Connection) => void
}

export default function GraphCanvas({ nodes, edges, onConnectEdge }: Props) {
  const rfNodes: RFNode[] = nodes.map((n) => ({
    id: String(n.id),
    position: n.position ?? { x: 0, y: 0 },
    data: { label: n.name ?? String(n.id) },
  }))
  const rfEdges: RFEdge[] = edges.map((e) => ({
    id: String(e.id),
    source: String(e.source),
    target: String(e.target),
  }))

  return (
    <ReactFlow
      nodes={rfNodes}
      edges={rfEdges}
      onConnect={onConnectEdge}
      fitView
      style={{ width: '100%', height: '100%' }}
    >
      <MiniMap />
      <Controls />
      <Background />
    </ReactFlow>
  )
}
