"use client";

import { useEffect, useRef, useState } from "react";
import type { Alert, ConnectionState } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/alerts";

export function useWebSocketStatus() {
  const [connectionState, setConnectionState] = useState<ConnectionState>("connecting");

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | null = null;
    let closed = false;

    const connect = () => {
      setConnectionState((current) => (current === "connecting" ? "connecting" : "reconnecting"));
      try {
        socket = new WebSocket(WS_URL);
        socket.onopen = () => setConnectionState("connected");
        socket.onerror = () => setConnectionState("reconnecting");
        socket.onclose = () => {
          if (closed) return;
          setConnectionState("reconnecting");
          retry = setTimeout(connect, 5000);
        };
      } catch {
        setConnectionState("disconnected");
        retry = setTimeout(connect, 5000);
      }
    };

    connect();
    return () => {
      closed = true;
      if (retry) clearTimeout(retry);
      socket?.close();
    };
  }, []);

  return { connectionState };
}

export function useAlertSocket(onAlert: (alert: Alert) => void) {
  const [connectionState, setConnectionState] = useState<ConnectionState>("connecting");
  const callbackRef = useRef(onAlert);
  callbackRef.current = onAlert;

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | null = null;
    let closed = false;

    const connect = () => {
      setConnectionState((current) => (current === "connecting" ? "connecting" : "reconnecting"));
      socket = new WebSocket(WS_URL);
      socket.onopen = () => setConnectionState("connected");
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          callbackRef.current(payload.alert || payload);
        } catch {
          // Ignore malformed backend messages.
        }
      };
      socket.onerror = () => setConnectionState("reconnecting");
      socket.onclose = () => {
        if (closed) return;
        setConnectionState("reconnecting");
        retry = setTimeout(connect, 5000);
      };
    };

    connect();
    return () => {
      closed = true;
      if (retry) clearTimeout(retry);
      socket?.close();
    };
  }, []);

  return { connectionState };
}
