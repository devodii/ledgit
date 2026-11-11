import type { Meta, StoryObj } from '@storybook/react';
import { MemoryRouter } from 'react-router-dom';
import { OrgCard } from './OrgCard';

const meta = {
  title: 'Domain/OrgCard',
  component: OrgCard,
  args: {
    slug: 'example-anchor-ltd',
    name: 'Example Anchor Ltd',
    domain: 'anchor.example.com',
    country: 'Exampleland',
    claimCount: 3,
  },
  decorators: [
    (Story) => (
      <MemoryRouter>
        <div style={{ width: 460, maxWidth: '100%' }}>
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
} satisfies Meta<typeof OrgCard>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const OneClaim: Story = { args: { claimCount: 1 } };
export const NoDetails: Story = { args: { domain: undefined, country: undefined } };
