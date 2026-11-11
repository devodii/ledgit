import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_LIVE, SYNTHETIC_MIXED, SYNTHETIC_NO_EVIDENCE } from '@/fixtures/evidenceChain';
import { EvidenceChain } from './EvidenceChain';

const meta = {
  title: 'Domain/EvidenceChain',
  component: EvidenceChain,
  parameters: { layout: 'padded' },
  args: { chain: SYNTHETIC_LIVE },
} satisfies Meta<typeof EvidenceChain>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Live: Story = {};
export const MixedResults: Story = { args: { chain: SYNTHETIC_MIXED } };
export const OpenAskNoEvidence: Story = { args: { chain: SYNTHETIC_NO_EVIDENCE } };
export const Narrow: Story = {
  args: { chain: SYNTHETIC_MIXED },
  parameters: { viewport: { defaultViewport: 'narrow' } },
};
