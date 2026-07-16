'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useToast } from '@/components/ui';

const API_ORIGIN = process.env.NEXT_PUBLIC_API_URL || '';
const API_PREFIX = '/api/v1';

function apiPath(path: string): string {
  return API_ORIGIN ? `${API_ORIGIN}${API_PREFIX}${path}` : `${API_PREFIX}${path}`;
}

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PROTECTED_ROUTES = ['/dashboard', '/roadmap', '/mentor', '/assess', '/upload'];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const { addToast } = useToast();

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('token');
      if (savedToken) {
        setToken(savedToken);
        try {
          const res = await fetch(apiPath('/auth/me'), {
            headers: { 'Authorization': `Bearer ${savedToken}` },
          });
          if (res.ok) {
            const data = await res.json();
            if (data.success) {
              setUser(data.data);
            } else {
              localStorage.removeItem('token');
              setToken(null);
            }
          } else {
            localStorage.removeItem('token');
            setToken(null);
          }
        } catch (err) {
          console.error('Failed to load user session', err);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  useEffect(() => {
    if (!loading) {
      const isProtected = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
      if (isProtected && !user) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in to access this page.',
          type: 'warning',
        });
        router.push('/login');
      }
    }
  }, [pathname, user, loading, router, addToast]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const res = await fetch(apiPath('/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(error.detail || 'Incorrect email or password');
      }

      const data = await res.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        setToken(data.token);
        setUser(data.user);
        addToast({
          title: 'Welcome back!',
          description: `Successfully signed in as ${data.user.name}`,
          type: 'success',
        });
        router.push('/dashboard');
        return true;
      }
      return false;
    } catch (err: any) {
      addToast({
        title: 'Sign In Failed',
        description: err.message || 'An error occurred during sign in.',
        type: 'error',
      });
      return false;
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    try {
      const res = await fetch(apiPath('/auth/signup'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(error.detail || 'Email already registered');
      }

      const data = await res.json();
      if (data.success) {
        addToast({
          title: 'Account Created',
          description: 'Registration successful. Please sign in.',
          type: 'success',
        });
        router.push('/login');
        return true;
      }
      return false;
    } catch (err: any) {
      addToast({
        title: 'Registration Failed',
        description: err.message || 'An error occurred during registration.',
        type: 'error',
      });
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    addToast({
      title: 'Signed Out',
      description: 'You have been successfully signed out.',
      type: 'success',
    });
    router.push('/');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
