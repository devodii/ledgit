import type { ClaimDetailData } from '@/api/client';
import { timeAgo } from '@/lib/format';
import { EmptyState } from '../../ui/EmptyState';
import { STATUS_COPY } from '../StatusBadge';
import styles from './VerdictTimeline.module.scss';

export interface VerdictTimelineProps {
  history: ClaimDetailData['history'];
}

export function VerdictTimeline({ history }: VerdictTimelineProps) {
  if (history.length === 0) {
    return (
      <EmptyState
        icon="hourglass"
        title="No history yet"
        description="The first daily check has not run for this claim."
      />
    );
  }
  return (
    <ol className={styles.timeline}>
      {history.map((entry) => (
        <li key={`${entry.changed_at}-${entry.to_status}`} className={styles.item}>
          <span className={styles.dot} aria-hidden="true" />
          <div>
            <p className={styles.title}>
              {entry.from_status ? `${STATUS_COPY[entry.from_status].label} → ` : 'First verdict: '}
              <strong>{STATUS_COPY[entry.to_status].label}</strong>
            </p>
            <p className={styles.reason}>{entry.reason}</p>
            <p className={styles.when}>
              <time dateTime={entry.changed_at}>{timeAgo(entry.changed_at)}</time>
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}
