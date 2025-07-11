import React, { createContext, useContext, useEffect, useRef, useState } from 'react'


interface WebSocketContextType {
  ws: WebSocket | null;
  isConnected: boolean;
  lastMessage: any;
}

const WebSocketContext = createContext<WebSocketContextType>({
  ws: null,
  isConnected: false,
  lastMessage: null
});

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Use a simple client_id (no authentication needed)
    const clientId = 'frontend-client';
    const wsUrl = (import.meta as any).env?.VITE_WS_URL
      ? (import.meta as any).env.VITE_WS_URL + `/ws/${clientId}`
      : `ws://localhost:8000/ws/${clientId}`;

    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;
    setWs(socket);

    socket.onopen = () => {
      setIsConnected(true);
      console.log('Connected to PowerShare WebSocket (native)');
    };
    socket.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from PowerShare WebSocket (native)');
    };
    socket.onerror = (e) => {
      setIsConnected(false);
      console.error('WebSocket error:', e);
    };
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        // Optionally, handle specific message types here
        if (data.type) {
          console.log(`WebSocket message [${data.type}]:`, data);
        } else {
          console.log('WebSocket message:', data);
        }
      } catch (err) {
        setLastMessage(event.data);
        console.log('WebSocket message (raw):', event.data);
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const value = {
    ws,
    isConnected,
    lastMessage
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
