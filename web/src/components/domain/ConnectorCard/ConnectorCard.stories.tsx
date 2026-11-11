import type { Meta, StoryObj } from '@storybook/react';
import { CONNECTORS } from '@/fixtures/connectors';
import { ConnectorCard } from './ConnectorCard';

const [youtube, transcripts, , stellarToml, , horizon, soroban, , , browser, lumenloop] =
  CONNECTORS;

const meta = {
  title: 'Domain/ConnectorCard',
  component: ConnectorCard,
  args: {
    connector: horizon,
    health: 'ok',
    detail: 'ledger 65,427,446',
    lastChecked: '2 minutes ago',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 420, maxWidth: '100%' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ConnectorCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Healthy: Story = {};
export const NotResponding: Story = {
  args: { connector: soroban, health: 'down', detail: 'getHealth: connection refused' },
};
export const NeedsHuman: Story = {
  args: {
    connector: browser,
    health: 'needs_human',
    detail: 'example.com showed a bot wall. Run with BROWSER_HEADFUL=1 and solve it.',
  },
};
export const Checking: Story = {
  args: { connector: transcripts, health: 'checking', detail: undefined, lastChecked: undefined },
};
export const Secondary: Story = {
  args: { connector: lumenloop, health: 'ok', detail: '2 projects' },
};
export const LongContent: Story = {
  args: {
    connector: {
      ...stellarToml,
      emits: ['StellarToml', 'TomlCurrency', 'SepEndpoint', 'AnotherVeryLongEmittedModelName'],
      allowedDomains: ['a-very-long-organisation-domain.example.com', 'another.example.org'],
    },
  },
};
export const NoDetail: Story = { args: { connector: youtube, detail: undefined } };
export const Narrow: Story = { parameters: { viewport: { defaultViewport: 'narrow' } } };

export const AllConnectors: Story = {
  parameters: { layout: 'padded' },
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: 16,
        width: '100%',
      }}
    >
      {CONNECTORS.map((connector) => (
        <ConnectorCard
          key={connector.name}
          connector={connector}
          health="ok"
          detail="synthetic healthcheck result"
          lastChecked="just now"
        />
      ))}
    </div>
  ),
};
