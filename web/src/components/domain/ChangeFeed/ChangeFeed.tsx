import type { ChangeItem } from '@/api/client';
import { EmptyState } from '../../ui/EmptyState';
import { ChangeFeedItem } from '../ChangeFeedItem';
import styles from './ChangeFeed.module.scss';

export interface ChangeFeedProps {
  changes: ChangeItem[];
}

export function ChangeFeed({ changes }: ChangeFeedProps) {
  if (changes.length === 0) {
    return (
      <EmptyState
        icon="hourglass"
        title="No verdict changes yet"
        description="Changes appear here after the daily check runs."
      />
    );
  }
  return (
    <ul className={styles.feed}>
      {changes.map((change) => (
        <ChangeFeedItem key={change.id} change={change} />
      ))}
    </ul>
  );
}
