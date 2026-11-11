import type { Meta, StoryObj } from '@storybook/react';
import { Icon } from './Icon';
import { ICON_PATHS, type IconName } from './icons';

const meta = {
  title: 'UI/Icon',
  component: Icon,
  args: { name: 'check', size: 'md' },
} satisfies Meta<typeof Icon>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Labelled: Story = { args: { name: 'info', label: 'Information' } };
export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: 16 }}>
      <Icon name="check" size="sm" />
      <Icon name="check" size="md" />
      <Icon name="check" size="lg" />
    </div>
  ),
};
export const AllIcons: Story = {
  parameters: { layout: 'padded' },
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
        gap: 16,
      }}
    >
      {(Object.keys(ICON_PATHS) as IconName[]).map((name) => (
        <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Icon name={name} />
          <code>{name}</code>
        </div>
      ))}
    </div>
  ),
};
export const Narrow: Story = {
  parameters: { viewport: { defaultViewport: 'narrow' } },
  render: AllIcons.render,
};
