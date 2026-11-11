import type { ReactNode } from 'react';
import styles from './Tag.module.scss';

export interface TagProps {
  children: ReactNode;
  mono?: boolean;
}

export function Tag({ children, mono = false }: TagProps) {
  return <span className={`${styles.tag} ${mono ? 'mono' : ''}`}>{children}</span>;
}
