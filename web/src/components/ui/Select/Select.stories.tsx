import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { Select } from './Select';

const meta = { title: 'UI/Select', component: Select } satisfies Meta<typeof Select>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo() {
  const [value, setValue] = useState('');
  return (
    <Select
      label="Countries"
      value={value}
      onChange={setValue}
      options={[
        { value: 'Exampleland', label: 'Exampleland' },
        { value: 'Examplestan', label: 'Examplestan' },
      ]}
    />
  );
}

export const Default: Story = {
  args: { label: 'Countries', value: '', onChange: () => {}, options: [] },
  render: () => <Demo />,
};
