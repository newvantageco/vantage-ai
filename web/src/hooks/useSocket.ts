"use client";

import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface UseSocketOptions {
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

interface SocketEvent {
  type: string;
  data: any;
  timestamp: number;
}

export function useSocket(
  url: string = process.env.NEXT_PUBLIC_SOCKET_URL || 'ws://localhost:8000',
  options: UseSocketOptions = {}
) {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 1000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<SocketEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]);

  const connect = () => {
    if (socketRef.current?.connected) return;

    try {
      socketRef.current = io(url, {
        autoConnect: false,
        reconnection: reconnect,
        reconnectionAttempts: reconnectAttempts,
        reconnectionDelay: reconnectDelay,
      });

      socketRef.current.on('connect', () => {
        setIsConnected(true);
        setError(null);
        console.log('Socket connected');
      });

      socketRef.current.on('disconnect', () => {
        setIsConnected(false);
        console.log('Socket disconnected');
      });

      socketRef.current.on('connect_error', (err) => {
        setError(err.message);
        console.error('Socket connection error:', err);
      });

      socketRef.current.on('reconnect', (attemptNumber) => {
        console.log('Socket reconnected after', attemptNumber, 'attempts');
      });

      socketRef.current.on('reconnect_error', (err) => {
        setError(err.message);
        console.error('Socket reconnection error:', err);
      });

      socketRef.current.on('reconnect_failed', () => {
        setError('Failed to reconnect to server');
        console.error('Socket reconnection failed');
      });

      // Listen for all events and store them
      socketRef.current.onAny((eventName, data) => {
        const event: SocketEvent = {
          type: eventName,
          data,
          timestamp: Date.now(),
        };
        setEvents(prev => [...prev.slice(-99), event]); // Keep last 100 events
      });

      socketRef.current.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const disconnect = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  };

  const emit = (event: string, data?: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('Socket not connected, cannot emit event:', event);
    }
  };

  const on = (event: string, callback: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  };

  const off = (event: string, callback?: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.off(event, callback);
    }
  };

  return {
    socket: socketRef.current,
    isConnected,
    events,
    error,
    connect,
    disconnect,
    emit,
    on,
    off,
  };
}

// Hook for realtime notifications
export function useRealtimeNotifications() {
  const { isConnected, emit, on, off } = useSocket();
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => {
    if (!isConnected) return;

    const handleNotification = (data: any) => {
      setNotifications(prev => [data, ...prev.slice(0, 49)]); // Keep last 50 notifications
    };

    on('notification', handleNotification);
    on('post_published', handleNotification);
    on('post_failed', handleNotification);
    on('ai_optimization_complete', handleNotification);
    on('new_follower', handleNotification);

    return () => {
      off('notification');
      off('post_published');
      off('post_failed');
      off('ai_optimization_complete');
      off('new_follower');
    };
  }, [isConnected, on, off]);

  const markAsRead = (notificationId: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, read: true }))
    );
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    markAsRead,
    markAllAsRead,
    clearNotifications,
  };
}

// Hook for realtime analytics
export function useRealtimeAnalytics() {
  const { isConnected, on, off } = useSocket();
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    if (!isConnected) return;

    const handleAnalyticsUpdate = (data: any) => {
      setAnalytics(data);
    };

    on('analytics_update', handleAnalyticsUpdate);
    on('engagement_update', handleAnalyticsUpdate);
    on('impression_update', handleAnalyticsUpdate);

    return () => {
      off('analytics_update');
      off('engagement_update');
      off('impression_update');
    };
  }, [isConnected, on, off]);

  return { analytics };
}
