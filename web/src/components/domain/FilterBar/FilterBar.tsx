import type { ClaimFilters } from '@/api/hooks';
import { FilterChip } from '../../ui/FilterChip';
import { SearchInput } from '../../ui/SearchInput';
import { Select } from '../../ui/Select';
import { SegmentedControl } from '../../ui/SegmentedControl';
import { STATUS_COPY, type VerdictStatus } from '../StatusBadge';
import styles from './FilterBar.module.scss';

const TYPES = [
  { value: 'partner_launch', label: 'Partner launches' },
  { value: 'roadmap', label: 'Roadmap' },
  { value: 'protocol_feature', label: 'Protocol features' },
  { value: 'open_ask', label: 'Open asks' },
];

export interface FilterBarProps {
  filters: ClaimFilters;
  onChange: (next: ClaimFilters) => void;
  statusCounts?: Partial<Record<VerdictStatus, number>>;
  countries: string[];
}

export function FilterBar({ filters, onChange, statusCounts = {}, countries }: FilterBarProps) {
  const set = (patch: Partial<ClaimFilters>) => onChange({ ...filters, ...patch });
  return (
    <div className={styles.bar}>
      <SearchInput
        value={filters.q ?? ''}
        onChange={(q) => set({ q })}
        placeholder="Search quotes, speakers, organisations"
      />
      <div className={styles.chips} role="group" aria-label="Verdict">
        {(Object.keys(STATUS_COPY) as VerdictStatus[]).map((status) => (
          <FilterChip
            key={status}
            active={filters.status === status}
            count={statusCounts[status]}
            onToggle={() => set({ status: filters.status === status ? undefined : status })}
          >
            {STATUS_COPY[status].label}
          </FilterChip>
        ))}
      </div>
      <div className={styles.selects}>
        <Select
          label="Claim types"
          value={filters.claimType ?? ''}
          onChange={(value) =>
            set({ claimType: (value || undefined) as ClaimFilters['claimType'] })
          }
          options={TYPES}
        />
        <Select
          label="Regions"
          value={filters.country ?? ''}
          onChange={(country) => set({ country: country || undefined })}
          options={countries.map((c) => ({ value: c, label: c }))}
        />
        <SegmentedControl
          label="Sort"
          value={filters.sort ?? 'newest'}
          onChange={(sort) => set({ sort })}
          options={[
            { value: 'newest', label: 'Newest' },
            { value: 'oldest', label: 'Oldest' },
          ]}
        />
      </div>
    </div>
  );
}
