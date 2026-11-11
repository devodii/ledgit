import type { ReactNode } from 'react';
import styles from './FilterChip.module.scss';

export interface FilterChipProps {
  active: boolean;
  onToggle: () => void;
  count?: number;
  children: ReactNode;
}

export function FilterChip({ active, onToggle, count, children }: FilterChipProps) {
  return (
    <button
      type="button"
      className={`${styles.chip} ${active ? styles.active : ''}`}
      aria-pressed={active}
      onClick={onToggle}
    >
      {children}
      {count !== undefined && <span className={styles.count}>{count}</span>}
    </button>
  );
}
