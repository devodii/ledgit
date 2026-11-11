import type { Meta, StoryObj } from '@storybook/react';
import { BackingRow } from './BackingRow';

const meta = { title: 'Domain/BackingRow', component: BackingRow } satisfies Meta<
  typeof BackingRow
>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Awarded: Story = {
  args: {
    found: true,
    projectUrl: 'https://example.com/scf/example',
    awardedUsd: 50000,
    source: 'scf',
  },
};
export const AmountUnknown: Story = {
  args: { found: true, projectUrl: 'https://example.com/scf/example' },
};
export const NotFoundRendersNothing: Story = { args: { found: false } };
