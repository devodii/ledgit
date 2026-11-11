import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import { Icon } from '../Icon';
import styles from './Toast.module.scss';

interface ToastItem {
  id: number;
  message: string;
}

const ToastContext = createContext<(message: string) => void>(() => {});

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const push = useCallback((message: string) => {
    const id = Date.now() + Math.random();
    setItems((current) => [...current, { id, message }]);
    setTimeout(() => setItems((current) => current.filter((item) => item.id !== id)), 3500);
  }, []);
  const value = useMemo(() => push, [push]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className={styles.region} role="status" aria-live="polite">
        {items.map((item) => (
          <div key={item.id} className={styles.toast}>
            <Icon name="check-circle" size="sm" />
            {item.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
