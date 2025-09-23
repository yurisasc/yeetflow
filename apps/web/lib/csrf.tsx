'use client';

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { SecurityUtils } from '@/lib/security';

interface CSRFContextType {
  token: string | null;
  refreshToken: () => void;
}

const CSRFContext = createContext<CSRFContextType | null>(null);

interface CSRFProviderProps {
  children: ReactNode;
}

export function CSRFProvider({ children }: CSRFProviderProps) {
  const [token, setToken] = useState<string | null>(null);

  const refreshToken = () => {
    const newToken = SecurityUtils.generateCSRFToken();
    setToken(newToken);
    // Store in sessionStorage for persistence during session
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('yeetflow_csrf_token', newToken);
    }
  };

  useEffect(() => {
    // Try to restore token from sessionStorage
    const storedToken = sessionStorage.getItem('yeetflow_csrf_token');
    if (storedToken) {
      setToken(storedToken);
    } else {
      refreshToken();
    }
  }, []);

  return (
    <CSRFContext.Provider value={{ token, refreshToken }}>
      {children}
    </CSRFContext.Provider>
  );
}

export function useCSRF() {
  const context = useContext(CSRFContext);
  if (!context) {
    throw new Error('useCSRF must be used within a CSRFProvider');
  }
  return context;
}
