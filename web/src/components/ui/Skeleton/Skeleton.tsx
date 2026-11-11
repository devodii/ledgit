import type { CSSProperties } from 'react';
import styles from './Skeleton.module.scss';

export interface SkeletonProps {
  width?: CSSProperties['width'];
  height?: CSSProperties['height'];
  circle?: boolean;
}

export function Skeleton({ width = '100%', height = '1em', circle = false }: SkeletonProps) {
  return (
    <span
      className={`${styles.skeleton} ${circle ? styles.circle : ''}`}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}
