import type { Meta, StoryObj } from '@storybook/react';
import { Tabs } from './Tabs';

const meta = { title: 'UI/Tabs', component: Tabs } satisfies Meta<typeof Tabs>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {
  args: {
    tabs: [
      { value: 'evidence', label: 'Evidence', content: <p>Evidence list goes here.</p> },
      { value: 'history', label: 'History', content: <p>Verdict history goes here.</p> },
    ],
  },
};
