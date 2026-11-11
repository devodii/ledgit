import type { Meta, StoryObj } from '@storybook/react';
import { LastUpdated } from './LastUpdated';

const meta = { title: 'Domain/LastUpdated', component: LastUpdated } satisfies Meta<
  typeof LastUpdated
>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Recent: Story = { args: { iso: new Date(Date.now() - 600_000).toISOString() } };
export const NeverChecked: Story = { args: { iso: null } };
