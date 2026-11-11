import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import type { ClaimFilters } from '@/api/hooks';
import { FilterBar } from './FilterBar';

const meta = {
  title: 'Domain/FilterBar',
  component: FilterBar,
  parameters: { layout: 'padded' },
} satisfies Meta<typeof FilterBar>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo({ initial }: { initial: ClaimFilters }) {
  const [filters, setFilters] = useState(initial);
  return (
    <FilterBar
      filters={filters}
      onChange={setFilters}
      countries={['Exampleland', 'Examplestan']}
      statusCounts={{ live: 14, testnet_only: 4, no_trace_found: 12, pending: 6, open_ask: 2 }}
    />
  );
}

export const Default: Story = {
  args: { filters: {}, onChange: () => {}, countries: [] },
  render: () => <Demo initial={{}} />,
};
export const WithFilters: Story = {
  args: { filters: {}, onChange: () => {}, countries: [] },
  render: () => <Demo initial={{ status: 'live', q: 'wallet', country: 'Exampleland' }} />,
};
