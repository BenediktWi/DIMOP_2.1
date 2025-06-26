import React from 'react'
import ReactFlow, { MiniMap, Controls, Background, Connection } from 'reactflow'
import 'reactflow/dist/style.css'


interface Props {
  nodes: any[]
  edges: any[]
  onConnectEdge: (connection: Connection) => void
}

export default function GraphCanvas({ nodes, edges, onConnectEdge }: Props) {
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
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
