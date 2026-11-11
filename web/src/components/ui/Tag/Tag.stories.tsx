import type { Meta, StoryObj } from '@storybook/react';
import { Tag } from './Tag';

const meta = {
  title: 'UI/Tag',
  component: Tag,
  args: { children: 'protocol_feature' },
} satisfies Meta<typeof Tag>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const Mono: Story = { args: { mono: true, children: 'anchor.example.com' } };
