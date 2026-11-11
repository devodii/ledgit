import type { ElementType, ReactNode } from 'react';
import styles from './VisuallyHidden.module.scss';

export interface VisuallyHiddenProps {
  as?: ElementType;
  children: ReactNode;
}

export function VisuallyHidden({ as: Tag = 'span', children }: VisuallyHiddenProps) {
  return <Tag className={styles.hidden}>{children}</Tag>;
}
