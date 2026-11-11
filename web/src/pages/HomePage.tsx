import { useMemo } from 'react';
import { useClaims, useEventSummary } from '@/api/hooks';
import { FilterBar } from '@/components/domain/FilterBar';
import { LoadMore } from '@/components/domain/LoadMore';
import { MethodologyCallout } from '@/components/domain/MethodologyCallout';
import { SummaryStrip } from '@/components/domain/SummaryStrip';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import type { VerdictStatus } from '@/api/client';
import { useClaimFilters } from '@/lib/useClaimFilters';
import { ClaimGrid } from './ClaimGrid';
import styles from './pages.module.scss';

export function HomePage() {
  const { filters, setFilters } = useClaimFilters();
  const claims = useClaims(filters);
  const summary = useEventSummary();
  const items = useMemo(
    () => claims.data?.pages.flatMap((page) => page.items) ?? [],
    [claims.data],
  );
  const counts = useMemo(
    () =>
      Object.fromEntries(
        (summary.data?.by_status ?? []).map((row) => [row.status, row.count]),
      ) as Partial<Record<VerdictStatus, number>>,
    [summary.data],
  );
  const countries = useMemo(
    () => [...new Set(items.map((item) => item.org_country).filter(Boolean))].sort(),
    [items],
  );

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>What did they say, and what does the network say today?</h1>
        <p>
          Specific, checkable claims made on stage at Meridian 2025, each with the speaker on video
          and the on-chain evidence checked daily.
        </p>
      </section>
      <MethodologyCallout />
      {summary.data && <SummaryStrip summary={summary.data} />}
      <FilterBar
        filters={filters}
        onChange={setFilters}
        statusCounts={counts}
        countries={countries}
      />
      {claims.isPending && (
        <div className={styles.grid} aria-busy="true">
          {Array.from({ length: 6 }, (_, index) => (
            <Skeleton key={index} height="26rem" />
          ))}
        </div>
      )}
      {claims.isError && <ErrorState onRetry={() => claims.refetch()} />}
      {claims.isSuccess && items.length === 0 && (
        <EmptyState
          title="No claims match these filters"
          description="Try removing a filter or searching for something else."
        />
      )}
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
