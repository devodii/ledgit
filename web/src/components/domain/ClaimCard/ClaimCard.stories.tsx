import type { Meta, StoryObj } from '@storybook/react';
import { ClaimCard } from './ClaimCard';

const meta = {
  title: 'Domain/ClaimCard',
  component: ClaimCard,
  args: {
    id: 'example-anchor-sep24',
    status: 'live',
    quote: 'SYNTHETIC QUOTE: Example Anchor Ltd will open deposits in Exampleland.',
    speaker: 'Example Speaker One',
    role: 'Chief Example Officer',
    orgName: 'Example Anchor Ltd',
    videoId: 'ard4j13AnnI',
    videoTitle: 'Meridian 2025 talk (demo clip)',
    startSeconds: 95,
    captionSource: 'manual',
    lastChecked: '2 hours ago',
    scfAwardedUsd: 50000,
    href: '#',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 460, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ClaimCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Live: Story = {};
export const TestnetOnly: Story = { args: { status: 'testnet_only', scfAwardedUsd: null } };
export const NoTrace: Story = { args: { status: 'no_trace_found', captionSource: 'auto' } };
export const Pending: Story = { args: { status: 'pending' } };
export const OpenAsk: Story = {
  args: { status: 'open_ask', speaker: undefined, role: undefined, scfAwardedUsd: null },
};
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };
