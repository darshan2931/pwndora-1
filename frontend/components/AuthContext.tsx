'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { getCurrentUser } from '@/services/api';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const res = await getCurrentUser();
          if (res.success) {
            setUser(res.data);
          }
        } catch (error) {
          console.error('Auth initialization failed', error);
          localStorage.removeItem('auth_token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = (token: string) => {
    localStorage.setItem('auth_token', token);
    getCurrentUser().then((res) => {
      if (res.success) setUser(res.data);
    }).catch(() => {
      localStorage.removeItem('auth_token');
    });
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
