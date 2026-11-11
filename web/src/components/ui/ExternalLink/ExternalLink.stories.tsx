import type { Meta, StoryObj } from '@storybook/react';
import { ExternalLink } from './ExternalLink';

const meta = {
  title: 'UI/ExternalLink',
  component: ExternalLink,
  args: { href: 'https://example.com', children: 'Example site' },
} satisfies Meta<typeof ExternalLink>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
