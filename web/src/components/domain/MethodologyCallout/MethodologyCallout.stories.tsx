import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { MethodologyCallout } from './MethodologyCallout';

const meta = {
  title: 'Domain/MethodologyCallout',
  component: MethodologyCallout,
  decorators: [
    (Story) => (
      <MemoryRouter>
        <div style={{ width: 560, maxWidth: '100%' }}>
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof MethodologyCallout>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
