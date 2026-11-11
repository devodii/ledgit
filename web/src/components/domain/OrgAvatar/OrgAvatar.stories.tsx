import type { Meta, StoryObj } from '@storybook/react';
import { OrgAvatar } from './OrgAvatar';

const meta = {
  title: 'Domain/OrgAvatar',
  component: OrgAvatar,
  args: { name: 'Example Anchor Ltd' },
} satisfies Meta<typeof OrgAvatar>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Medium: Story = {};
export const Small: Story = { args: { size: 'sm' } };
export const Large: Story = { args: { size: 'lg' } };
