import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { LoadMore } from './LoadMore';

const meta = {
  title: 'Domain/LoadMore',
  component: LoadMore,
  args: { onLoadMore: fn(), hasMore: true, loading: false },
} satisfies Meta<typeof LoadMore>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const Loading: Story = { args: { loading: true } };
export const End: Story = { args: { hasMore: false } };
