export type ConnectorHealth = 'ok' | 'down' | 'needs_human' | 'checking';

export interface ConnectorInfo {
  name: string;
  role: 'primary' | 'secondary';
  summary: string;
  allowedDomains: string[];
  rateLimitRps: number;
  emits: string[];
}

export const CONNECTORS: ConnectorInfo[] = [
  {
    name: 'youtube',
    role: 'primary',
    summary: 'Lists event videos and reads titles, dates and descriptions.',
    allowedDomains: ['youtube.com', 'googleapis.com', 'ytimg.com'],
    rateLimitRps: 2,
    emits: ['VideoMeta'],
  },
  {
    name: 'transcripts',
    role: 'primary',
    summary: 'Fetches timed captions and records whether they are manual or auto.',
    allowedDomains: ['youtube.com', 'googlevideo.com'],
    rateLimitRps: 0.5,
    emits: ['Transcript'],
  },
  {
    name: 'sessions',
    role: 'primary',
    summary: 'Reads official agenda pages for speakers, roles and organisations.',
    allowedDomains: ['meridian.stellar.org', 'stellar.org'],
    rateLimitRps: 0.5,
    emits: ['SessionPage'],
  },
  {
    name: 'stellar_toml',
    role: 'primary',
    summary: 'Reads stellar.toml (SEP-1) for accounts, currencies and SEP endpoints.',
    allowedDomains: ['the organisation domain'],
    rateLimitRps: 2,
    emits: ['StellarToml'],
  },
  {
    name: 'sep_info',
    role: 'primary',
    summary: 'Calls SEP-6, 24, 31 and 38 info endpoints and records if they respond.',
    allowedDomains: ['hosts declared in stellar.toml'],
    rateLimitRps: 2,
    emits: ['SepProbe'],
  },
  {
    name: 'horizon',
    role: 'primary',
    summary: 'Account existence, asset holders and supply on pubnet and testnet.',
    allowedDomains: ['horizon.stellar.lobstr.co', 'horizon-testnet.stellar.org'],
    rateLimitRps: 5,
    emits: ['AssetStats', 'AccountInfo'],
  },
  {
    name: 'soroban',
    role: 'primary',
    summary: 'Contract existence and recent invocation events within RPC retention.',
    allowedDomains: ['mainnet.sorobanrpc.com', 'soroban-testnet.stellar.org'],
    rateLimitRps: 3,
    emits: ['ContractStatus'],
  },
  {
    name: 'stellar_expert',
    role: 'primary',
    summary: 'Free directory lookups that map organisations to known addresses.',
    allowedDomains: ['api.stellar.expert'],
    rateLimitRps: 1,
    emits: ['DirectoryEntry'],
  },
  {
    name: 'scf',
    role: 'primary',
    summary: 'Public Stellar Community Fund project pages and awarded amounts.',
    allowedDomains: ['communityfund.stellar.org'],
    rateLimitRps: 1,
    emits: ['ScfProject'],
  },
  {
    name: 'browser',
    role: 'primary',
    summary: 'Headless Chromium for pages that need JavaScript. Stops at any bot wall.',
    allowedDomains: ['any, on request'],
    rateLimitRps: 0.5,
    emits: ['RenderedPage'],
  },
  {
    name: 'lumenloop',
    role: 'secondary',
    summary: 'Ecosystem directory and SCF submissions over MCP. Enrichment only.',
    allowedDomains: ['mcp.lumenloop.com', 'lumenloop.com'],
    rateLimitRps: 2,
    emits: ['LumenLoopProject'],
  },
  {
    name: 'stellarlight',
    role: 'secondary',
    summary: 'Project directory with contracts, assets and SCF totals. Enrichment only.',
    allowedDomains: ['stellarlight.xyz'],
    rateLimitRps: 1,
    emits: ['StellarLightProject'],
  },
];
