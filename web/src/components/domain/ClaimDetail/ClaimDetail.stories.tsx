import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { SYNTHETIC_DETAIL } from '@/fixtures/claims';
import { ToastProvider } from '../../ui/Toast';
import { ClaimDetail } from './ClaimDetail';

const meta = {
  title: 'Domain/ClaimDetail',
  component: ClaimDetail,
  parameters: { layout: 'padded' },
  decorators: [
    (Story) => (
      <MemoryRouter>
        <ToastProvider>
          <Story />
        </ToastProvider>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof ClaimDetail>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Live: Story = { args: { claim: SYNTHETIC_DETAIL } };
export const NoEvidence: Story = {
  args: {
    claim: {
      ...SYNTHETIC_DETAIL,
      evidence: [],
      history: [],
      verdict: {
        status: 'no_trace_found',
        reason: 'No on-chain or public reference could be linked yet.',
        checked_at: SYNTHETIC_DETAIL.verdict.checked_at,
      },
    },
  },
};
export const Narrow: Story = {
  args: { claim: SYNTHETIC_DETAIL },
  parameters: { viewport: { defaultViewport: 'narrow' } },
};
