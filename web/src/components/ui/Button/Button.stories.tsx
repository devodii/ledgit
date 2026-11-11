import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'UI/Button',
  component: Button,
  args: { children: 'Save changes', onClick: fn() },
  argTypes: { variant: { control: 'inline-radio', options: ['primary', 'secondary', 'subtle'] } },
} satisfies Meta<typeof Button>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  play: async ({ canvasElement, args }) => {
    await userEvent.click(within(canvasElement).getByRole('button'));
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};
export const Secondary: Story = { args: { variant: 'secondary' } };
export const Subtle: Story = { args: { variant: 'subtle' } };
export const Small: Story = { args: { size: 'sm' } };
export const Large: Story = { args: { size: 'lg' } };
export const WithIcon: Story = { args: { icon: 'external', children: 'Open source' } };
export const Loading: Story = { args: { loading: true } };
export const Disabled: Story = { args: { disabled: true } };
export const LongContent: Story = {
  args: { children: 'A button label that is much longer than anyone would reasonably want to use' },
  decorators: [
    (Story) => (
      <div style={{ maxWidth: 320 }}>
        <Story />
      </div>
    ),
  ],
};
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };
