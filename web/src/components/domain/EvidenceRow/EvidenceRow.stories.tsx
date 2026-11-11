import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_DETAIL } from '@/fixtures/claims';
import { ToastProvider } from '../../ui/Toast';
import { EvidenceRow } from './EvidenceRow';

const [anchor, asset] = SYNTHETIC_DETAIL.evidence;

const meta = {
  title: 'Domain/EvidenceRow',
  component: EvidenceRow,
  args: { evidence: anchor },
  decorators: [
    (Story) => (
      <ToastProvider>
        <ul style={{ width: 520, maxWidth: '100%', padding: 0, margin: 0 }}>
          <Story />
        </ul>
      </ToastProvider>
    ),
  ],
} satisfies Meta<typeof EvidenceRow>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Anchor: Story = {};
export const Asset: Story = { args: { evidence: asset } };
export const NotChecked: Story = { args: { evidence: { ...asset, latest_observation: null } } };
export const TestnetOnly: Story = {
  args: {
    evidence: {
      ...asset,
      kind: 'soroban_contract',
      network: 'testnet',
      latest_observation: {
        checked_at: '2025-01-05T06:00:00Z',
        result: 'testnet_only',
        detail: { summary: 'deployed on testnet, not on mainnet' },
      },
    },
  },
};
export const CouldNotRun: Story = {
  args: {
    evidence: {
      ...asset,
      latest_observation: {
        checked_at: '2025-01-05T06:00:00Z',
        result: 'error',
        detail: { summary: 'check could not run: horizon returned 503' },
      },
    },
  },
};
