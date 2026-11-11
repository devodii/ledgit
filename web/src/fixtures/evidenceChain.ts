export type ObservationResult = 'live' | 'testnet_only' | 'not_found' | 'error';

export interface ChainEvidence {
  id: string;
  kind: 'asset_issuer' | 'soroban_contract' | 'anchor' | 'protocol_upgrade';
  network: 'pubnet' | 'testnet';
  ref: string;
  foundVia: string;
  result: ObservationResult | null;
  detail: string;
  checkedAt: string;
}

export interface ChainData {
  claim: { quote: string; speaker: string; role: string };
  org: { name: string; domain: string; country: string };
  evidence: ChainEvidence[];
  verdict: {
    status: 'live' | 'testnet_only' | 'no_trace_found' | 'pending' | 'open_ask';
    reason: string;
  };
}

export const SYNTHETIC_LIVE: ChainData = {
  claim: {
    quote: 'SYNTHETIC QUOTE: Example Anchor Ltd will open deposits in Exampleland.',
    speaker: 'Example Speaker One',
    role: 'Chief Example Officer',
  },
  org: { name: 'Example Anchor Ltd', domain: 'anchor.example.com', country: 'Exampleland' },
  evidence: [
    {
      id: 'e1',
      kind: 'anchor',
      network: 'pubnet',
      ref: 'anchor.example.com',
      foundVia: 'synthetic fixture',
      result: 'live',
      detail: 'stellar.toml reachable, SEP-24 info responded',
      checkedAt: '2025-01-05 06:00 UTC',
    },
    {
      id: 'e2',
      kind: 'asset_issuer',
      network: 'pubnet',
      ref: 'EXMP-GEXAMPLEISSUERSYNTHETIC0000000000000000000000000000000',
      foundVia: 'synthetic fixture',
      result: 'live',
      detail: '120 holders, non-zero supply',
      checkedAt: '2025-01-05 06:00 UTC',
    },
  ],
  verdict: {
    status: 'live',
    reason: 'Found live on Stellar mainnet: a SEP endpoint responds and the asset has holders.',
  },
};

export const SYNTHETIC_MIXED: ChainData = {
  claim: {
    quote: 'SYNTHETIC QUOTE: Example Wallet Inc is shipping a smart contract account.',
    speaker: 'Example Speaker Two',
    role: 'Founder',
  },
  org: { name: 'Example Wallet Inc', domain: 'wallet.example.com', country: 'Examplestan' },
  evidence: [
    {
      id: 'e1',
      kind: 'soroban_contract',
      network: 'testnet',
      ref: 'CEXAMPLECONTRACTSYNTHETIC00000000000000000000000000000000',
      foundVia: 'synthetic fixture',
      result: 'testnet_only',
      detail: 'Deployed on testnet, not on mainnet',
      checkedAt: '2025-01-05 06:00 UTC',
    },
    {
      id: 'e2',
      kind: 'anchor',
      network: 'pubnet',
      ref: 'wallet.example.com',
      foundVia: 'synthetic fixture',
      result: 'not_found',
      detail: 'No stellar.toml found',
      checkedAt: '2025-01-05 06:00 UTC',
    },
    {
      id: 'e3',
      kind: 'asset_issuer',
      network: 'pubnet',
      ref: 'EXWL-GEXAMPLEWALLETISSUERSYNTHETIC00000000000000000000000',
      foundVia: 'synthetic fixture',
      result: 'error',
      detail: 'Horizon returned 503',
      checkedAt: '2025-01-05 06:00 UTC',
    },
  ],
  verdict: {
    status: 'testnet_only',
    reason: 'Found on testnet, not yet on mainnet. Other checks found nothing or could not run.',
  },
};

export const SYNTHETIC_NO_EVIDENCE: ChainData = {
  claim: {
    quote: 'SYNTHETIC QUOTE: We need someone to build an example indexer.',
    speaker: 'Example Speaker Five',
    role: 'Ecosystem Lead',
  },
  org: { name: 'Example Foundation', domain: 'foundation.example.com', country: 'Exampleland' },
  evidence: [],
  verdict: { status: 'open_ask', reason: 'Requested on stage, no builder identified.' },
};
