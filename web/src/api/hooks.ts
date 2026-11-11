import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { api, EVENT_SLUG, unwrap, type ClaimType, type VerdictStatus } from './client';

export interface ClaimFilters {
  status?: VerdictStatus;
  claimType?: ClaimType;
  country?: string;
  org?: string;
  q?: string;
  sort?: 'newest' | 'oldest';
}

export function useClaims(filters: ClaimFilters) {
  return useInfiniteQuery({
    queryKey: ['claims', filters],
    initialPageParam: undefined as string | undefined,
    queryFn: async ({ pageParam }) =>
      unwrap(
        await api.GET('/api/v1/claims', {
          params: {
            query: {
              status: filters.status,
              claim_type: filters.claimType,
              country: filters.country,
              org: filters.org,
              q: filters.q || undefined,
              sort: filters.sort,
              cursor: pageParam,
              limit: 12,
            },
          },
        }),
      ),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
  });
}

export function useClaim(id: string) {
  return useQuery({
    queryKey: ['claim', id],
    queryFn: async () =>
      unwrap(await api.GET('/api/v1/claims/{claim_id}', { params: { path: { claim_id: id } } })),
  });
}

export function useOrg(slug: string) {
  return useQuery({
    queryKey: ['org', slug],
    queryFn: async () =>
      unwrap(await api.GET('/api/v1/orgs/{slug}', { params: { path: { slug } } })),
  });
}

export function useEventSummary() {
  return useQuery({
    queryKey: ['summary', EVENT_SLUG],
    queryFn: async () =>
      unwrap(
        await api.GET('/api/v1/events/{slug}/summary', { params: { path: { slug: EVENT_SLUG } } }),
      ),
  });
}

export function useChanges() {
  return useInfiniteQuery({
    queryKey: ['changes'],
    initialPageParam: undefined as string | undefined,
    queryFn: async ({ pageParam }) =>
      unwrap(await api.GET('/api/v1/changes', { params: { query: { cursor: pageParam } } })),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
  });
}

export function useMeta() {
  return useQuery({
    queryKey: ['meta'],
    queryFn: async () => unwrap(await api.GET('/api/v1/meta')),
  });
}

export function useAdminTasks() {
  return useQuery({
    queryKey: ['admin-tasks'],
    refetchInterval: 5000,
    queryFn: async () => unwrap(await api.GET('/api/v1/admin/tasks')),
  });
}
