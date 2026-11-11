import type { ClaimDetailData } from '@/api/client';
import { formatDateTime, timeAgo } from '@/lib/format';
import { EmptyState } from '../../ui/EmptyState';
import { Icon } from '../../ui/Icon';
import { STATUS_COPY, StatusBadge } from '../StatusBadge';
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
    <ol className={styles.timeline} aria-label="Verdict history, newest first">
      {history.map((entry, index) => {
        const isCurrent = index === 0;
        return (
          <li
            key={`${entry.changed_at}-${entry.to_status}`}
            className={`${styles.item} ${styles[entry.to_status]} ${isCurrent ? styles.current : ''}`}
          >
            <div className={styles.rail} aria-hidden="true">
              <span className={styles.dot}>
                <Icon name={STATUS_COPY[entry.to_status].icon} size="sm" />
              </span>
              {index < history.length - 1 && <span className={styles.line} />}
            </div>
            <div className={styles.body}>
              <div className={styles.head}>
                <StatusBadge status={entry.to_status} />
                {isCurrent && <span className={styles.now}>Current</span>}
              </div>
              <p className={styles.change}>
                {entry.from_status
                  ? `Changed from ${STATUS_COPY[entry.from_status].label.toLowerCase()}`
                  : 'First verdict for this claim'}
              </p>
              <p className={styles.reason}>{entry.reason}</p>
              <p className={styles.when}>
                <time dateTime={entry.changed_at}>{formatDateTime(entry.changed_at)}</time>
                <span aria-hidden="true"> · </span>
                <span>{timeAgo(entry.changed_at)}</span>
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
