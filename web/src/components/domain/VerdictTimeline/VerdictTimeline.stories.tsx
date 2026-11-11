import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_DETAIL } from '@/fixtures/claims';
import { VerdictTimeline } from './VerdictTimeline';

const meta = {
  title: 'Domain/VerdictTimeline',
  component: VerdictTimeline,
  decorators: [
    (Story) => (
      <div style={{ width: 560, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof VerdictTimeline>;
export default meta;
type Story = StoryObj<typeof meta>;

const day = 86400_000;
const at = (daysAgo: number) => new Date(Date.now() - daysAgo * day).toISOString();
const claim_id = 'example-anchor-sep24';

export const TwoSteps: Story = { args: { history: SYNTHETIC_DETAIL.history } };

export const LongHistory: Story = {
  args: {
    history: [
      {
        claim_id,
        from_status: 'testnet_only',
        to_status: 'live',
        reason: 'The contract is now deployed on mainnet with recent invocations.',
        changed_at: at(2),
      },
      {
        claim_id,
        from_status: 'no_trace_found',
        to_status: 'testnet_only',
        reason: 'The contract was found on testnet, not on mainnet.',
        changed_at: at(40),
      },
      {
        claim_id,
        from_status: 'pending',
        to_status: 'no_trace_found',
        reason: 'None of the checks found a trace.',
        changed_at: at(75),
      },
      {
        claim_id,
        from_status: null,
        to_status: 'pending',
        reason: 'The talk was given 3 days ago, too recent to assess.',
        changed_at: at(90),
      },
    ],
  },
};

export const SingleEntry: Story = { args: { history: [SYNTHETIC_DETAIL.history[1]] } };
export const Empty: Story = { args: { history: [] } };
export const Narrow: Story = {
  args: { history: SYNTHETIC_DETAIL.history },
  parameters: { viewport: { defaultViewport: 'narrow' } },
};
