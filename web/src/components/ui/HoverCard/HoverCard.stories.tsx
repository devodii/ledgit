import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../Button';
import { HoverCard } from './HoverCard';

const meta = { title: 'UI/HoverCard', component: HoverCard } satisfies Meta<typeof HoverCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    content: (
      <div style={{ padding: 16, background: '#12151c', borderRadius: 12 }}>
        Hover or focus the trigger to see this card.
      </div>
    ),
    children: <Button variant="secondary">Hover me</Button>,
  },
};
