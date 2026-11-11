import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_SUMMARY } from '@/fixtures/claims';
import { SummaryStrip } from './SummaryStrip';

const meta = {
  title: 'Domain/SummaryStrip',
  component: SummaryStrip,
  parameters: { layout: 'padded' },
  args: { summary: SYNTHETIC_SUMMARY },
} satisfies Meta<typeof SummaryStrip>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };
