import type { Meta, StoryObj } from '@storybook/react';
import { VerdictBanner } from './VerdictBanner';

const meta = {
  title: 'Domain/VerdictBanner',
  component: VerdictBanner,
  args: {
    status: 'live',
    reason: '2 of 2 checks found live. anchor: stellar.toml reachable, sep24 responded.',
    checkedAt: new Date(Date.now() - 3600_000).toISOString(),
  },
  decorators: [
    (Story) => (
      <div style={{ width: 560, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof VerdictBanner>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Live: Story = {};
export const TestnetOnly: Story = {
  args: { status: 'testnet_only', reason: 'Found on testnet, not on mainnet.' },
};
export const NoTrace: Story = {
  args: { status: 'no_trace_found', reason: 'None of the checks found a trace.' },
};
export const Pending: Story = {
  args: { status: 'pending', reason: 'The talk was given 3 days ago, too recent to assess.' },
};
export const OpenAsk: Story = {
  args: {
    status: 'open_ask',
    reason: 'Requested on stage, no builder identified.',
    checkedAt: null,
  },
};
