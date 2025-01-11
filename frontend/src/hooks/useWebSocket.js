import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import io from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'ws://localhost:8000/ws';

export const useWebSocket = () => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const clientId = uuidv4();
    const socketInstance = new WebSocket(`${SOCKET_URL}/${clientId}`);

    socketInstance.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setError(null);
    };

    socketInstance.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    socketInstance.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Failed to connect to chat server');
      setConnected(false);
    };

    setSocket(socketInstance);

    // Cleanup on unmount
    return () => {
      if (socketInstance) {
        socketInstance.close();
      }
    };
  }, []);

  const sendMessage = (event, data) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ event, data }));
    } else {
      console.error('WebSocket is not connected');
    }
  };

  return {
    socket,
    connected,
    error,
    sendMessage
  };
};
