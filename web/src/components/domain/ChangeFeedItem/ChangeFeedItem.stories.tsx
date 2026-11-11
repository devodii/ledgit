import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { SYNTHETIC_CHANGES } from '@/fixtures/claims';
import { ChangeFeedItem } from './ChangeFeedItem';

const meta = {
  title: 'Domain/ChangeFeedItem',
  component: ChangeFeedItem,
  decorators: [
    (Story) => (
      <MemoryRouter>
        <ul style={{ width: 520, maxWidth: '100%', padding: 0, margin: 0 }}>
          <Story />
        </ul>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof ChangeFeedItem>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Transition: Story = { args: { change: SYNTHETIC_CHANGES[0] } };
export const FirstVerdict: Story = { args: { change: SYNTHETIC_CHANGES[1] } };
