import type { ChangeItem } from '@/api/client';
import { timeAgo } from '@/lib/format';
import { Link } from '../../ui/Link';
import { StatusBadge } from '../StatusBadge';
import styles from './ChangeFeedItem.module.scss';

export interface ChangeFeedItemProps {
  change: ChangeItem;
}

export function ChangeFeedItem({ change }: ChangeFeedItemProps) {
  return (
    <li className={styles.item}>
      <div className={styles.head}>
        <Link to={`/claims/${change.claim_id}`}>{change.org_name}</Link>
        <time dateTime={change.changed_at} className={styles.when}>
          {timeAgo(change.changed_at)}
        </time>
      </div>
      <p>{change.summary}</p>
      <div className={styles.transition}>
        {change.from_status ? (
          <StatusBadge status={change.from_status} />
        ) : (
          <span>First verdict</span>
        )}
        <span aria-hidden="true">→</span>
        <StatusBadge status={change.to_status} />
      </div>
      <p className={styles.reason}>{change.reason}</p>
    </li>
  );
}
