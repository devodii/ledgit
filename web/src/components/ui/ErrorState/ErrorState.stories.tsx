import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';
import { ErrorState } from './ErrorState';

const meta = { title: 'UI/ErrorState', component: ErrorState } satisfies Meta<typeof ErrorState>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {};
export const WithRetry: Story = { args: { onRetry: fn() } };
