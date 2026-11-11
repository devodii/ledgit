import createClient from 'openapi-fetch';
import type { components, paths } from './generated/schema';

export const api = createClient<paths>({ baseUrl: '' });

export type ClaimSummary = components['schemas']['ClaimSummary'];
export type ClaimDetailData = components['schemas']['ClaimDetail'];
export type OrgDetailData = components['schemas']['OrgDetail'];
export type OrgSummary = components['schemas']['OrgSummary'];
export type EventSummaryData = components['schemas']['EventSummary'];
export type ChangeItem = components['schemas']['ChangeItem'];
export type TaskListData = components['schemas']['TaskList'];
export type VerdictStatus = ClaimSummary['status'];
export type ClaimType = ClaimSummary['claim_type'];

export const EVENT_SLUG = import.meta.env.VITE_EVENT_SLUG ?? 'meridian-2025';
export const GITHUB_REPO = import.meta.env.VITE_GITHUB_REPO ?? 'devodii/ledgit';

export class ApiError extends Error {}

export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.data === undefined) throw new ApiError(`Request returned ${result.response.status}`);
  return result.data;
}
