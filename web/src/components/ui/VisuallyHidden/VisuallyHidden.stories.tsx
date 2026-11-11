import type { Meta, StoryObj } from '@storybook/react';
import { VisuallyHidden } from './VisuallyHidden';

const meta = { title: 'UI/VisuallyHidden', component: VisuallyHidden } satisfies Meta<
  typeof VisuallyHidden
>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: 'Only screen readers read this' },
  render: (args) => (
    <p>
      Visible text <VisuallyHidden {...args} />
    </p>
  ),
};
