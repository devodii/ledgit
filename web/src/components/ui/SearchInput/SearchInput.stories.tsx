import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { SearchInput } from './SearchInput';

const meta = { title: 'UI/SearchInput', component: SearchInput } satisfies Meta<typeof SearchInput>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo({ initial }: { initial: string }) {
  const [value, setValue] = useState(initial);
  return (
    <div style={{ width: 360, maxWidth: '100%' }}>
      <SearchInput value={value} onChange={setValue} />
      <p style={{ marginTop: 8, color: '#a3abbd' }}>Committed value: {value || '(empty)'}</p>
    </div>
  );
}

export const Empty: Story = {
  args: { value: '', onChange: () => {} },
  render: () => <Demo initial="" />,
};
export const WithValue: Story = {
  args: { value: '', onChange: () => {} },
  render: () => <Demo initial="wallet" />,
};
