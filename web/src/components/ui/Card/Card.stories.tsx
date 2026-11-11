import type { Meta, StoryObj } from '@storybook/react';
import { Card } from './Card';

const meta = {
  title: 'UI/Card',
  component: Card,
  args: { children: 'Card content' },
} satisfies Meta<typeof Card>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const Unpadded: Story = { args: { padded: false } };
