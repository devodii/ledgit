import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from '@storybook/test';
import { IconButton } from './IconButton';

const meta = {
  title: 'UI/IconButton',
  component: IconButton,
  args: { icon: 'copy', label: 'Copy address', onClick: fn() },
} satisfies Meta<typeof IconButton>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Subtle: Story = {
  play: async ({ canvasElement, args }) => {
    await userEvent.click(within(canvasElement).getByRole('button', { name: 'Copy address' }));
    await expect(args.onClick).toHaveBeenCalled();
  },
};
export const Secondary: Story = { args: { variant: 'secondary' } };
export const Small: Story = { args: { size: 'sm' } };
export const Large: Story = { args: { size: 'lg' } };
export const Disabled: Story = { args: { disabled: true } };
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };
