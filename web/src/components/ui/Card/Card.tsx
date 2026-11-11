import type { ElementType, ReactNode } from 'react';
import styles from './Card.module.scss';

export interface CardProps {
  as?: ElementType;
  padded?: boolean;
  children: ReactNode;
  className?: string;
}

export function Card({ as: Tag = 'div', padded = true, children, className }: CardProps) {
  return (
    <Tag
      className={[styles.card, padded ? styles.padded : '', className].filter(Boolean).join(' ')}
    >
      {children}
    </Tag>
  );
}
