import type { Meta, StoryObj } from '@storybook/react';
import { SYNTHETIC_DETAIL } from '@/fixtures/claims';
import { ToastProvider } from '../../ui/Toast';
import { EvidenceList } from './EvidenceList';

const meta = {
  title: 'Domain/EvidenceList',
  component: EvidenceList,
  decorators: [
    (Story) => (
      <ToastProvider>
        <div style={{ width: 560, maxWidth: '100%' }}>
          <Story />
        </div>
      </ToastProvider>
    ),
  ],
} satisfies Meta<typeof EvidenceList>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = { args: { evidence: SYNTHETIC_DETAIL.evidence } };
export const Empty: Story = { args: { evidence: [] } };
