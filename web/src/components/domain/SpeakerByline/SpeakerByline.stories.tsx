import type { Meta, StoryObj } from '@storybook/react';
import { SpeakerByline } from './SpeakerByline';

const meta = { title: 'Domain/SpeakerByline', component: SpeakerByline } satisfies Meta<
  typeof SpeakerByline
>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Full: Story = {
  args: { name: 'Example Speaker One', role: 'Chief Example Officer', org: 'Example Anchor Ltd' },
};
export const NameOnly: Story = { args: { name: 'Example Speaker Two' } };
export const NotStated: Story = {};
