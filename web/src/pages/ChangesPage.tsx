import { useMemo } from 'react';
import { useChanges } from '@/api/hooks';
import { ChangeFeed } from '@/components/domain/ChangeFeed';
import { LoadMore } from '@/components/domain/LoadMore';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import styles from './pages.module.scss';

export function ChangesPage() {
  const changes = useChanges();
  const items = useMemo(
    () => changes.data?.pages.flatMap((page) => page.items) ?? [],
    [changes.data],
  );
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>Verdict changes</h1>
        <p>Every time a daily check changes what we report about a claim, it appears here.</p>
      </section>
      {changes.isPending && <Skeleton height="20rem" />}
      {changes.isError && <ErrorState onRetry={() => changes.refetch()} />}
      {changes.isSuccess && <ChangeFeed changes={items} />}
      {changes.isSuccess && items.length > 0 && (
        <LoadMore
          hasMore={Boolean(changes.hasNextPage)}
          loading={changes.isFetchingNextPage}
          onLoadMore={() => changes.fetchNextPage()}
        />
      )}
    </div>
  );
}
