import type { Meta, StoryObj } from '@storybook/react';
import { Spinner } from './Spinner';

const meta = { title: 'UI/Spinner', component: Spinner } satisfies Meta<typeof Spinner>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Small: Story = { args: { size: 'sm' } };
export const Large: Story = { args: { size: 'lg', label: 'Loading claims' } };
