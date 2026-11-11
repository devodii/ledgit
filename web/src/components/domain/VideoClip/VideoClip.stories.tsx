import type { Meta, StoryObj } from '@storybook/react';
import { VideoClip } from './VideoClip';

const meta = {
  title: 'Domain/VideoClip',
  component: VideoClip,
  args: {
    videoId: 'ard4j13AnnI',
    startSeconds: 95,
    title: "It's Never Been Better to Build On Stellar | Meridian 2025",
  },
  decorators: [
    (Story) => (
      <div style={{ width: 480, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof VideoClip>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Poster: Story = {};
export const FromStart: Story = { args: { startSeconds: 0 } };
export const LongTimestamp: Story = { args: { startSeconds: 3725 } };
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };
