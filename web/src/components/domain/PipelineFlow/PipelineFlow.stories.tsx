import type { Meta, StoryObj } from '@storybook/react';
import { PipelineFlow } from './PipelineFlow';

const meta = {
  title: 'Domain/PipelineFlow',
  component: PipelineFlow,
  parameters: { layout: 'padded' },
} satisfies Meta<typeof PipelineFlow>;
export default meta;
type Story = StoryObj<typeof meta>;

export const AllHealthy: Story = {};
export const WithProblems: Story = {
  args: {
    health: {
      soroban: 'down',
      browser: 'needs_human',
      lumenloop: 'checking',
    },
  },
};
export const Short: Story = { args: { height: 480 } };
export const Narrow: Story = {
  parameters: { viewport: { defaultViewport: 'narrow' } },
  args: { height: 520 },
};
