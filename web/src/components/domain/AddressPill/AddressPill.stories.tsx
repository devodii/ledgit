import type { Meta, StoryObj } from '@storybook/react';
import { ToastProvider } from '../../ui/Toast';
import { AddressPill } from './AddressPill';

const meta = {
  title: 'Domain/AddressPill',
  component: AddressPill,
  args: {
    value: 'CEXAMPLECONTRACTSYNTHETIC00000000000000000000000000000000',
    network: 'pubnet',
    href: 'https://example.com',
  },
  decorators: [
    (Story) => (
      <ToastProvider>
        <Story />
      </ToastProvider>
    ),
  ],
} satisfies Meta<typeof AddressPill>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Mainnet: Story = {};
export const Testnet: Story = { args: { network: 'testnet' } };
export const NoExplorer: Story = { args: { href: null } };
