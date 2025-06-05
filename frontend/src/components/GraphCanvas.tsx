import React from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
} from 'react-flow-renderer'
import 'react-flow-renderer/dist/style.css'
import 'react-flow-renderer/dist/theme-default.css'

interface Props {
  nodes: any[]
  edges: any[]
  onChange: (state: { nodes: any[]; edges: any[] }) => void
}

export default function GraphCanvas({ nodes, edges, onChange }: Props) {
  const onConnect = (params: any) => onChange({ nodes, edges: addEdge(params, edges) })
  return (
    <ReactFlow nodes={nodes} edges={edges} onConnect={onConnect} fitView className="h-5/6">
      <MiniMap />
      <Controls />
      <Background />
    </ReactFlow>
  )
}
