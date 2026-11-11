import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { SegmentedControl } from './SegmentedControl';

const meta = { title: 'UI/SegmentedControl', component: SegmentedControl } satisfies Meta<
  typeof SegmentedControl
>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo() {
  const [value, setValue] = useState<'newest' | 'oldest'>('newest');
  return (
    <SegmentedControl
      label="Sort"
      value={value}
      onChange={setValue}
      options={[
        { value: 'newest', label: 'Newest' },
        { value: 'oldest', label: 'Oldest' },
      ]}
    />
  );
}

export const Default: Story = {
  args: { label: 'Sort', value: 'newest', onChange: () => {}, options: [] },
  render: () => <Demo />,
};
