import type { Meta, StoryObj } from '@storybook/react';
import { ToastProvider } from '../Toast';
import { CopyButton } from './CopyButton';

const meta = {
  title: 'UI/CopyButton',
  component: CopyButton,
  args: {
    value: 'GEXAMPLEISSUERSYNTHETIC000000000000000000000000000000000',
    label: 'Copy address',
  },
  decorators: [
    (Story) => (
      <ToastProvider>
        <Story />
      </ToastProvider>
    ),
  ],
} satisfies Meta<typeof CopyButton>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
