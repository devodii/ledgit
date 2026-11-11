import type { ReactNode } from 'react';
import { Icon, type IconName } from '../Icon';
import styles from './EmptyState.module.scss';

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: IconName;
  action?: ReactNode;
}

export function EmptyState({ title, description, icon = 'search', action }: EmptyStateProps) {
  return (
    <div className={styles.empty} role="status">
      <Icon name={icon} size="lg" />
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {action}
    </div>
  );
}
