import React, { useEffect, useState, useCallback, useRef } from 'react';

// --- Re-defining all components/hooks/types internally to resolve import errors ---

// components/GraphCanvas.tsx - Placeholder (now using SVG for graph visualization)
interface Node {
  id: string;
  position: { x: number; y: number };
  data: { label: string };
}

interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

interface GraphCanvasProps {
  nodes: Node[];
  edges: Edge[];
  onChange: (state: { nodes: Node[]; edges: Edge[] }) => void;
}

const initialNodes: Node[] = [
  { id: '1', position: { x: 50, y: 50 }, data: { label: 'Start Node' } },
  { id: '2', position: { x: 200, y: 150 }, data: { label: 'Process A' } },
  { id: '3', position: { x: 350, y: 50 }, data: { label: 'Process B' } },
  { id: '4', position: { x: 200, y: 250 }, data: { label: 'End Node' } },
];
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', label: 'Flow 1' },
  { id: 'e2-3', source: '2', target: '3', label: 'Flow 2' },
  { id: 'e2-4', source: '2', target: '4', label: 'Flow 3' }
];

export function GraphCanvas({ nodes, edges, onChange }: GraphCanvasProps) {
  const [currentNodes, setCurrentNodes] = useState(nodes.length > 0 ? nodes : initialNodes);
  const [currentEdges, setCurrentEdges] = useState(edges.length > 0 ? edges : initialEdges);

  // This simple canvas doesn't support interactive changes, but logs them
  const handleNodeClick = (nodeId: string) => {
    console.log(`Node ${nodeId} clicked`);
  };

  return (
    <div className="w-full h-full bg-white rounded-lg p-4 relative overflow-hidden">
      <svg className="absolute top-0 left-0 w-full h-full">
        {/* Render edges */}
        {currentEdges.map(edge => {
          const sourceNode = currentNodes.find(n => n.id === edge.source);
          const targetNode = currentNodes.find(n => n.id === edge.target);

          if (!sourceNode || !targetNode) return null;

          // Simple line for now; for arrows, would need more complex SVG paths
          return (
            <line
              key={edge.id}
              x1={sourceNode.position.x + 25} // approximate center of node
              y1={sourceNode.position.y + 25}
              x2={targetNode.position.x + 25}
              y2={targetNode.position.y + 25}
              stroke="#6b7280" // Tailwind gray-500
              strokeWidth="2"
              markerEnd="url(#arrowhead)" // For an arrow
            />
          );
        })}

        {/* Define arrowhead marker */}
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
          </marker>
        </defs>

        {/* Render nodes */}
        {currentNodes.map(node => (
          <g
            key={node.id}
            transform={`translate(${node.position.x}, ${node.position.y})`}
            className="cursor-pointer"
            onClick={() => handleNodeClick(node.id)}
          >
            <rect
              x="0"
              y="0"
              width="100"
              height="50"
              rx="8" // rounded corners
              ry="8"
              fill="#bfdbfe" // Tailwind blue-200
              stroke="#3b82f6" // Tailwind blue-500
              strokeWidth="2"
            />
            <text
              x="50"
              y="30"
              fill="#1e40af" // Tailwind blue-800
              textAnchor="middle"
              alignmentBaseline="middle"
              className="text-sm font-semibold"
            >
              {node.data.label}
            </text>
          </g>
        ))}
      </svg>
      <div className="absolute bottom-2 right-2 flex space-x-2">
        {/* Placeholder for minimap/controls if we were using a library */}
      </div>
    </div>
  );
}

// components/MaterialTable.tsx - Placeholder
interface Material {
  id: string;
  name: string;
  quantity: number;
}

interface MaterialTableProps {
  materials: Material[];
  onDelete: (id: string) => void; // Placeholder prop
}

export function MaterialTable({ materials, onDelete }: MaterialTableProps) {
  // Mock data if materials prop is empty
  const mockMaterials: Material[] = [
    { id: 'm1', name: 'Steel Beam', quantity: 10 },
    { id: 'm2', name: 'Concrete Mix', quantity: 50 },
    { id: 'm3', name: 'Glass Panel', quantity: 25 }
  ];

  const displayMaterials = materials.length > 0 ? materials : mockMaterials;

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {displayMaterials.map((material) => (
            <tr key={material.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{material.id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{material.name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{material.quantity}</td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onDelete(material.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


// components/useUndoRedo.ts - Placeholder
export function useUndoRedo<T>(initialState: T, limit: number = 50) {
  const [state, setCurrentState] = useState<T>(initialState);
  const history = useRef<T[]>([initialState]);
  const historyPointer = useRef<number>(0);

  const setState = useCallback((newState: T | ((prevState: T) => T)) => {
    setCurrentState((prev) => {
      const resolvedState = typeof newState === 'function' ? (newState as (prevState: T) => T)(prev) : newState;

      // Only add to history if the state has actually changed
      if (JSON.stringify(resolvedState) !== JSON.stringify(prev)) {
        // Truncate history after current pointer if new state is added
        history.current = history.current.slice(0, historyPointer.current + 1);
        // Add new state to history
        history.current.push(resolvedState);
        // Enforce limit
        if (history.current.length > limit) {
          history.current = history.current.slice(history.current.length - limit);
        }
        historyPointer.current = history.current.length - 1;
      }
      return resolvedState;
    });
  }, [limit]);

  const undo = useCallback(() => {
    if (historyPointer.current > 0) {
      historyPointer.current -= 1;
      setCurrentState(history.current[historyPointer.current]);
    }
  }, []);

  const redo = useCallback(() => {
    if (historyPointer.current < history.current.length - 1) {
      historyPointer.current += 1;
      setCurrentState(history.current[historyPointer.current]);
    }
  }, []);

  return { state, setState, undo, redo };
}


// wsMessage.ts - Placeholder
// Defines the types for WebSocket messages and a helper function to apply them.

// Re-exporting Node and Edge from here so they are available without import from GraphCanvas if moved
// (though in this single file structure, direct access is fine)
export interface Node {
  id: string;
  position: { x: number; y: number };
  data: { label: string };
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface Material {
  id: string;
  name: string;
  quantity: number;
}

export interface GraphState {
  nodes: Node[];
  edges: Edge[];
  materials: Material[];
}

// Simplified WsMessage types for demonstration
export type WsMessage =
  | { type: 'initial_graph_state'; payload: GraphState }
  | { type: 'node_added'; payload: Node }
  | { type: 'node_removed'; payload: { id: string } }
  | { type: 'edge_added'; payload: Edge }
  | { type: 'material_updated'; payload: Material };

// Function to apply WebSocket messages to the current state
export function applyWsMessage(prevState: GraphState, message: WsMessage): GraphState {
  console.log('Applying WS message:', message);
  switch (message.type) {
    case 'initial_graph_state':
      return message.payload;
    case 'node_added':
      return { ...prevState, nodes: [...prevState.nodes, message.payload] };
    case 'node_removed':
      return { ...prevState, nodes: prevState.nodes.filter(node => node.id !== message.payload.id) };
    case 'edge_added':
      return { ...prevState, edges: [...prevState.edges, message.payload] };
    case 'material_updated':
      const existingMaterialIndex = prevState.materials.findIndex(m => m.id === message.payload.id);
      if (existingMaterialIndex > -1) {
        const updatedMaterials = [...prevState.materials];
        updatedMaterials[existingMaterialIndex] = message.payload;
        return { ...prevState, materials: updatedMaterials };
      } else {
        return { ...prevState, materials: [...prevState.materials, message.payload] };
      }
    default:
      console.warn('Unknown WS message type:', message.type);
      return prevState;
  }
}

// --- End of internal component definitions ---


// Main App component
export default function App() {
  const { state, setState, undo, redo } = useUndoRedo<GraphState>({ nodes: [], edges: [], materials: [] }, 50);
  const [error, setError] = useState<string | null>(null);

  // useRef to keep track of the WebSocket instance across renders
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const MAX_RECONNECT_ATTEMPTS = 10; // Max attempts before giving up
  const RECONNECT_DELAY_MS = 2000; // Initial delay for reconnection (2 seconds)

  const [projectId] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('project');
    if (query) {
      localStorage.setItem('projectId', query);
      return query;
    }
    return localStorage.getItem('projectId') ?? '1';
  });

  // Function to establish WebSocket connection
  const connectWebSocket = useCallback(() => {
    // Ensure only one connection attempt is active
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${scheme}://localhost:8000/ws/projects/${projectId}`;
    console.log(`Attempting to connect WebSocket to: ${wsUrl}`);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connection opened successfully!');
      reconnectAttempts.current = 0; // Reset attempts on successful connection
      setError(null); // Clear any connection errors
    };

    ws.onmessage = ev => {
      try {
        const msg: WsMessage = JSON.parse(ev.data);
        setState(prev => applyWsMessage(prev, msg));
      } catch (e) {
        console.error('Invalid WS message or parsing error:', ev.data, e);
      }
    };

    ws.onclose = (event) => {
      console.log(`WebSocket connection closed: Code ${event.code}, Reason: ${event.reason}`);
      wsRef.current = null; // Clear the ref
      // Attempt to reconnect if not explicitly closed (e.g., by component unmount)
      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS && !event.wasClean) {
        const delay = RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts.current); // Exponential back-off
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1})`);
        reconnectAttempts.current += 1;
        setTimeout(connectWebSocket, Math.min(delay, 30000)); // Cap delay at 30 seconds
        setError('WebSocket disconnected. Attempting to reconnect...');
      } else if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
        setError('WebSocket disconnected. Max reconnection attempts reached.');
        console.error('Max reconnection attempts reached. Please refresh the page.');
      }
    };

    ws.onerror = (errorEvent) => {
      console.error('WebSocket error:', errorEvent);
      ws.close(); // Force close to trigger onclose for reconnection logic
      setError('WebSocket error. Attempting to reconnect...');
    };

    wsRef.current = ws; // Store the WebSocket instance in the ref
  }, [projectId, setState]); // Dependencies for connectWebSocket

  // Effect to manage WebSocket lifecycle
  useEffect(() => {
    connectWebSocket(); // Establish connection on mount

    return () => {
      // Cleanup function: Close connection when component unmounts
      if (wsRef.current) {
        // Use a clean close code (1000 for normal closure) to avoid triggering reconnect logic
        wsRef.current.close(1000, 'Component unmounted');
        wsRef.current = null;
      }
    };
  }, [connectWebSocket]); // Dependency on connectWebSocket ensures it's called if the function reference changes (unlikely here)


  useEffect(() => {
    fetch(`/projects/${projectId}/graph`)
      .then(r => {
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}`);
        }
        return r.json();
      })
      .then(setState)
      .catch(() => setError('Failed to load project data'));
  }, [projectId, setState]); // Added setState to dependencies as it's used inside


  if (error) {
    return <div className="p-4 text-red-600 font-semibold text-center">{error}</div>;
  }

  return (
    <div className="flex h-screen w-full font-sans bg-gray-50"> {/* Added font-sans for Inter font and bg-gray-50 */}
      <div className="w-2/3 h-full p-4 flex flex-col"> {/* Added flex-col for column layout */}
        <div className="bg-white rounded-lg shadow-lg flex-grow min-h-[500px] relative border border-gray-200">
          <GraphCanvas nodes={state.nodes} edges={state.edges} onChange={setState} />
        </div>
        <div className="p-4 flex justify-center space-x-4 bg-gray-100 rounded-b-lg shadow-inner">
          <button onClick={undo} className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75">
            Undo
          </button>
          <button onClick={redo} className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75">
            Redo
          </button>
        </div>
      </div>
      <div className="w-1/3 h-full p-4 overflow-y-auto flex flex-col">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Materials</h2>
        <MaterialTable materials={state.materials} onDelete={() => {}} />
      </div>
    </div>
  );
}
