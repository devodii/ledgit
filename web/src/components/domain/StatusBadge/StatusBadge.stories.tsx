import type { Meta, StoryObj } from '@storybook/react';
import { StatusBadge, type VerdictStatus } from './StatusBadge';

const meta = { title: 'Domain/StatusBadge', component: StatusBadge } satisfies Meta<
  typeof StatusBadge
>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Live: Story = { args: { status: 'live' } };
export const TestnetOnly: Story = { args: { status: 'testnet_only' } };
export const NoTraceFound: Story = { args: { status: 'no_trace_found' } };
export const Pending: Story = { args: { status: 'pending' } };
export const OpenAsk: Story = { args: { status: 'open_ask' } };
export const All: Story = {
  args: { status: 'live' },
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'flex-start' }}>
      {(['live', 'testnet_only', 'no_trace_found', 'pending', 'open_ask'] as VerdictStatus[]).map(
        (s) => (
          <StatusBadge key={s} status={s} />
        ),
      )}
    </div>
  ),
};
