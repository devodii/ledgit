import { Button } from '../../ui/Button';
import styles from './LoadMore.module.scss';

export interface LoadMoreProps {
  hasMore: boolean;
  loading: boolean;
  onLoadMore: () => void;
}

export function LoadMore({ hasMore, loading, onLoadMore }: LoadMoreProps) {
  if (!hasMore) return <p className={styles.end}>You have reached the end.</p>;
  return (
    <div className={styles.wrap}>
      <Button variant="secondary" loading={loading} onClick={onLoadMore}>
        Load more
      </Button>
    </div>
  );
}
