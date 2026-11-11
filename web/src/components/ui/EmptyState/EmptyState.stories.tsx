import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../Button';
import { EmptyState } from './EmptyState';

const meta = {
  title: 'UI/EmptyState',
  component: EmptyState,
  args: {
    title: 'No claims match these filters',
    description: 'Try removing a filter or searching for something else.',
  },
} satisfies Meta<typeof EmptyState>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const WithAction: Story = {
  args: { action: <Button variant="secondary">Clear filters</Button> },
};
