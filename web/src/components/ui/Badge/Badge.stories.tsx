import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './Badge';

const meta = { title: 'UI/Badge', component: Badge, args: { children: 'Badge' } } satisfies Meta<
  typeof Badge
>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Neutral: Story = {};
export const Accent: Story = { args: { tone: 'accent' } };
export const Success: Story = { args: { tone: 'success' } };
export const Warning: Story = { args: { tone: 'warning' } };
export const Danger: Story = { args: { tone: 'danger' } };
