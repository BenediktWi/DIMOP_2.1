import React from 'react'
import ReactFlow, { MiniMap, Controls, Background, addEdge } from 'reactflow'
import 'reactflow/dist/style.css'


interface Props {
  nodes: any[]
  edges: any[]
  onChange: (state: { nodes: any[]; edges: any[] }) => void
}

export default function GraphCanvas({ nodes, edges, onChange }: Props) {
  const onConnect = (params: any) => onChange({ nodes, edges: addEdge(params, edges) })
  return (
    <ReactFlow nodes={nodes} edges={edges} onConnect={onConnect} fitView className="h-full">
      <MiniMap />
      <Controls />
      <Background />
    </ReactFlow>
  )
}
