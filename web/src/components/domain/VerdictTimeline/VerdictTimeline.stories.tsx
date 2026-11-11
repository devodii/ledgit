import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_DETAIL } from '@/fixtures/claims';
import { VerdictTimeline } from './VerdictTimeline';

const meta = {
  title: 'Domain/VerdictTimeline',
  component: VerdictTimeline,
  decorators: [
    (Story) => (
      <div style={{ width: 520, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof VerdictTimeline>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = { args: { history: SYNTHETIC_DETAIL.history } };
export const Empty: Story = { args: { history: [] } };
