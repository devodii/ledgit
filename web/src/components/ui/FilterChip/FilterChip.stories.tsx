import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { FilterChip } from './FilterChip';

const meta = {
  title: 'UI/FilterChip',
  component: FilterChip,
  args: { children: 'Found live', active: false, onToggle: fn() },
} satisfies Meta<typeof FilterChip>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Inactive: Story = {};
export const Active: Story = { args: { active: true } };
export const WithCount: Story = { args: { count: 12 } };
