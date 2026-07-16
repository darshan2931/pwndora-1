'use client';

import { createContext, useContext, useState, ReactNode, ReactElement } from 'react';

type ToastType = 'default' | 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  id: string;
  title: string;
  description?: string;
  type?: ToastType;
  action?: React.ReactNode;
}

interface ToastState {
  toasts: ToastProps[];
}

export const ToastContext = createContext<{
  toastState: ToastState;
  addToast: (toast: Omit<ToastProps, 'id'>) => void;
  removeToast: (id: string) => void;
}>({
  toastState: { toasts: [] },
  addToast: () => {},
  removeToast: () => {}
});

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toastState, setToastState] = useState<ToastState>({ toasts: [] });

  const addToast = (toast: Omit<ToastProps, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToastState(prev => ({
      toasts: [...prev.toasts, { ...toast, id }]
    }));

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      removeToast(id);
    }, 5000);
  };

  const removeToast = (id: string) => {
    setToastState(prev => ({
      toasts: prev.toasts.filter(t => t.id !== id)
    }));
  };

  return (
    <ToastContext.Provider value={{ toastState, addToast, removeToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

const toastTypeVariants: Record<ToastType, string> = {
  default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
  success: 'bg-accent/10 text-accent border-accent/20',
  error: 'bg-error/10 text-error border-error/20',
  warning: 'bg-warning/10 text-warning border-warning/20',
  info: 'bg-primary/10 text-primary border-primary/20'
};

function ToastContainer() {
  const { toastState, removeToast } = useToast();

  return (
    <div className="fixed z-50 flex flex-col items-end p-4 pointer-events-none">
      <div className="space-y-4 w-full max-w-xs pointer-events-auto">
        {toastState.toasts.map(toast => (
          <div
            key={toast.id}
            onClick={() => removeToast(toast.id)}
            className={`
              flex w-full items-start space-x-4 rounded-lg p-4
              ${toastTypeVariants[toast.type || 'default']}
              shadow-lg transform transition-all duration-300
              hover:scale-[1.02]
              cursor-pointer
            `}
            role="alert"
          >
            <div className="flex-shrink-0 flex items-center h-6 w-6">
              {toast.type === 'success' && (
                <svg className="h-5 w-5 text-accent" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              {toast.type === 'error' && (
                <svg className="h-5 w-5 text-error" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              {toast.type === 'warning' && (
                <svg className="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              {toast.type === 'info' && (
                <svg className="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              {(toast.type === 'default' || !toast.type) && (
                <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>
            <div className="flex-1 space-y-2">
              <div className="text-sm font-medium">{toast.title}</div>
              {toast.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {toast.description}
                </p>
              )}
              {toast.action && (
                <div className="flex justify-end mt-2">
                  {toast.action}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}