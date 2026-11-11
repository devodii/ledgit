import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { Link } from './Link';

const meta = {
  title: 'UI/Link',
  component: Link,
  args: { to: '/methodology', children: 'Read the methodology' },
  decorators: [
    (Story) => (
      <MemoryRouter>
        <Story />
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof Link>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
