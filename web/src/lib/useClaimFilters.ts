import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { ClaimFilters } from '@/api/hooks';

export function useClaimFilters(fixed: Partial<ClaimFilters> = {}) {
  const [params, setParams] = useSearchParams();
  const filters = useMemo<ClaimFilters>(
    () => ({
      q: params.get('q') ?? undefined,
      status: (params.get('status') as ClaimFilters['status']) ?? undefined,
      claimType: (params.get('type') as ClaimFilters['claimType']) ?? undefined,
      country: params.get('country') ?? undefined,
      sort: (params.get('sort') as ClaimFilters['sort']) ?? undefined,
      ...fixed,
    }),
    [params, fixed],
  );
  const setFilters = useCallback(
    (next: ClaimFilters) => {
      const out = new URLSearchParams();
      if (next.q) out.set('q', next.q);
      if (next.status) out.set('status', next.status);
      if (next.claimType) out.set('type', next.claimType);
      if (next.country) out.set('country', next.country);
      if (next.sort && next.sort !== 'newest') out.set('sort', next.sort);
      setParams(out, { replace: true });
    },
    [setParams],
  );
  return { filters, setFilters };
}
