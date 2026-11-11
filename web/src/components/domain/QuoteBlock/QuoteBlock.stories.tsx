import type { Meta, StoryObj } from '@storybook/react';
import { QuoteBlock } from './QuoteBlock';

const meta = {
  title: 'Domain/QuoteBlock',
  component: QuoteBlock,
  args: {
    quote: 'SYNTHETIC QUOTE: Example Anchor Ltd will open deposits in Exampleland.',
    speaker: 'Example Speaker One',
    role: 'Chief Example Officer',
    captionSource: 'manual',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 520, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof QuoteBlock>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Manual: Story = {};
export const AutoCaptions: Story = { args: { captionSource: 'auto' } };
export const NoSpeaker: Story = { args: { speaker: undefined, role: undefined } };
export const Long: Story = {
  args: {
    quote: 'SYNTHETIC QUOTE: '.concat(
      'A long statement that keeps going so the wrapping behaviour can be reviewed. '.repeat(4),
    ),
  },
};
