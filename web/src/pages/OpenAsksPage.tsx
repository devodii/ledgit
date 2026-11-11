import { useMemo } from 'react';
import { useClaims } from '@/api/hooks';
import { LoadMore } from '@/components/domain/LoadMore';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { ClaimGrid } from './ClaimGrid';
import styles from './pages.module.scss';

const FILTERS = { claimType: 'open_ask' as const };

export function OpenAsksPage() {
  const claims = useClaims(FILTERS);
  const items = useMemo(
    () => claims.data?.pages.flatMap((page) => page.items) ?? [],
    [claims.data],
  );
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>Open asks</h1>
        <p>
          Things speakers said the ecosystem needs, where no builder was named. A builder could pick
          these up.
        </p>
      </section>
      {claims.isPending && <Skeleton height="26rem" />}
      {claims.isError && <ErrorState onRetry={() => claims.refetch()} />}
      {claims.isSuccess && items.length === 0 && <EmptyState title="No open asks recorded" />}
      {items.length > 0 && <ClaimGrid claims={items} />}
      {claims.isSuccess && items.length > 0 && (
        <LoadMore
          hasMore={Boolean(claims.hasNextPage)}
          loading={claims.isFetchingNextPage}
          onLoadMore={() => claims.fetchNextPage()}
        />
      )}
    </div>
  );
}
