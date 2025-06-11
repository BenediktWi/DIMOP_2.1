import React, { useEffect, useState, useRef } from 'react'
import GraphCanvas from './components/GraphCanvas'
import MaterialTable from './components/MaterialTable'
import useUndoRedo from './components/useUndoRedo'
import { applyWsMessage, GraphState, WsMessage } from './wsMessage'

// Main App component
export default function App() {
  const { state, setState, undo, redo } = useUndoRedo<GraphState>({ nodes: [], edges: [], materials: [] }, 50);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const MAX_RECONNECT_ATTEMPTS = 10;
  const RECONNECT_DELAY_MS = 2000;

  const [projectId] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('project');
    if (query) {
      localStorage.setItem('projectId', query);
      return query;
    }
    return localStorage.getItem('projectId') ?? '1';
  });

  // Function to establish WebSocket connection, including reconnection logic
  const connectWebSocket = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return; // Already connected or connecting
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
  }, [projectId, setState]); // Dependencies for connectWebSocket function


  // Effect hook to manage the WebSocket lifecycle: connect on mount, disconnect on unmount
  useEffect(() => {
    connectWebSocket(); // Establish connection when component mounts

    // Cleanup function: This runs when the component unmounts
    return () => {
      if (wsRef.current) {
        // Use a clean close code (1000) to explicitly close without triggering reconnection
        wsRef.current.close(1000, 'Component unmounted');
        wsRef.current = null;
      }
    };
  }, [connectWebSocket]); // Dependency on connectWebSocket ensures it's called if the function reference changes

  // Effect for fetching initial graph data
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
  }, [projectId, setState]);


  if (error) {
    return <div className="p-4 text-red-600 font-semibold text-center">{error}</div>;
  }

  return (
    <div className="flex h-screen w-full font-sans bg-gray-50">
      <div className="w-2/3 h-full p-4 flex flex-col">
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

