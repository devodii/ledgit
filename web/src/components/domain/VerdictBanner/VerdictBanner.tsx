import { timeAgo } from '@/lib/format';
import { StatusBadge, type VerdictStatus } from '../StatusBadge';
import styles from './VerdictBanner.module.scss';

export interface VerdictBannerProps {
  status: VerdictStatus;
  reason: string;
  checkedAt?: string | null;
}

export function VerdictBanner({ status, reason, checkedAt }: VerdictBannerProps) {
  return (
    <section className={`${styles.banner} ${styles[status]}`} aria-label="Verdict">
      <StatusBadge status={status} />
      <p className={styles.reason}>{reason}</p>
      <p className={styles.checked}>Last checked {timeAgo(checkedAt)}</p>
    </section>
  );
}
