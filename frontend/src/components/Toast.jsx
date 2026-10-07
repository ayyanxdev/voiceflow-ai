import { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';

const ToastContext = createContext();

export function useToast() {
  return useContext(ToastContext);
}

const icons = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
};

const colors = {
  success: { bg: 'rgba(16, 185, 129, 0.1)', border: '#10b981', text: '#059669' },
  error: { bg: 'rgba(239, 68, 68, 0.1)', border: '#ef4444', text: '#dc2626' },
  info: { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6', text: '#2563eb' },
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={addToast}>
      {children}
      <div className="toast-container">
        {toasts.map(toast => {
          const Icon = icons[toast.type];
          const color = colors[toast.type];
          return (
            <div
              key={toast.id}
              className="toast"
              style={{ borderLeftColor: color.border }}
            >
              <Icon size={18} style={{ color: color.border, flexShrink: 0 }} />
              <p className="text-sm font-medium flex-1" style={{ color: 'var(--text-primary)' }}>
                {toast.message}
              </p>
              <button
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded hover:bg-black/5 transition-colors"
                style={{ color: 'var(--text-muted)' }}
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
