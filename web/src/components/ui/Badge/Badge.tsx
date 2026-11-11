import type { ReactNode } from 'react';
import styles from './Badge.module.scss';

export interface BadgeProps {
  tone?: 'neutral' | 'accent' | 'success' | 'warning' | 'danger';
  children: ReactNode;
}

export function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={`${styles.badge} ${styles[tone]}`}>{children}</span>;
}
