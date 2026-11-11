import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { SYNTHETIC_CHANGES } from '@/fixtures/claims';
import { ChangeFeed } from './ChangeFeed';

const meta = {
  title: 'Domain/ChangeFeed',
  component: ChangeFeed,
  decorators: [
    (Story) => (
      <MemoryRouter>
        <div style={{ width: 560, maxWidth: '100%' }}>
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof ChangeFeed>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = { args: { changes: SYNTHETIC_CHANGES } };
export const Empty: Story = { args: { changes: [] } };
