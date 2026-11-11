import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { Footer } from './Footer';

const meta = {
  title: 'Layout/Footer',
  component: Footer,
  parameters: { layout: 'fullscreen' },
  decorators: [
    (Story) => (
      <MemoryRouter>
        <Story />
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof Footer>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {
  args: {
    lastVerifiedAt: new Date(Date.now() - 7200_000).toISOString(),
    dataVersion: 'f4ea4760ad28',
  },
};
export const NotVerifiedYet: Story = { args: {} };
