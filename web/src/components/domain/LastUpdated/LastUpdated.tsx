import { timeAgo } from '@/lib/format';
import styles from './LastUpdated.module.scss';

export interface LastUpdatedProps {
  iso?: string | null;
  label?: string;
}

export function LastUpdated({ iso, label = 'Last checked' }: LastUpdatedProps) {
  return (
    <span className={styles.updated}>
      {label} {iso ? <time dateTime={iso}>{timeAgo(iso)}</time> : 'not yet'}
    </span>
  );
}
