import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../Button';
import { ToastProvider, useToast } from './Toast';

function Trigger() {
  const toast = useToast();
  return <Button onClick={() => toast('Address copied')}>Show toast</Button>;
}

const meta = {
  title: 'UI/Toast',
  component: ToastProvider,
  decorators: [(Story) => <Story />],
} satisfies Meta<typeof ToastProvider>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: <Trigger /> },
};
