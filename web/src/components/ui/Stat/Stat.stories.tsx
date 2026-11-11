import type { Meta, StoryObj } from '@storybook/react';
import { Stat } from './Stat';

const meta = {
  title: 'UI/Stat',
  component: Stat,
  args: { label: 'Claims checked', value: 38 },
} satisfies Meta<typeof Stat>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const WithDelta: Story = { args: { delta: '+3 this week' } };
