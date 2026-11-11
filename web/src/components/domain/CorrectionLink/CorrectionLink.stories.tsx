import type { Meta, StoryObj } from '@storybook/react';
import { CorrectionLink } from './CorrectionLink';

const meta = {
  title: 'Domain/CorrectionLink',
  component: CorrectionLink,
  args: {
    repo: 'devodii/ledgit',
    claimId: 'example-anchor-sep24',
    quote: 'SYNTHETIC QUOTE: Example Anchor Ltd will open deposits in Exampleland.',
  },
} satisfies Meta<typeof CorrectionLink>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
