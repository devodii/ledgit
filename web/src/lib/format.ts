export function timeAgo(iso: string | null | undefined, now = new Date()): string {
  if (!iso) return 'not checked yet';
  const seconds = Math.max(0, Math.floor((now.getTime() - new Date(iso).getTime()) / 1000));
  const units: Array<[number, string]> = [
    [86400, 'day'],
    [3600, 'hour'],
    [60, 'minute'],
  ];
  for (const [size, name] of units) {
    if (seconds >= size) {
      const value = Math.floor(seconds / size);
      return `${value} ${name}${value === 1 ? '' : 's'} ago`;
    }
  }
  return 'just now';
}

export function formatUsd(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return '';
  return `$${Number(value).toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
}

export function truncateMiddle(value: string, head = 6, tail = 6): string {
  return value.length <= head + tail + 1 ? value : `${value.slice(0, head)}…${value.slice(-tail)}`;
}

export function correctionUrl(repo: string, claimId: string, quote: string): string {
  const title = encodeURIComponent(`Correction: ${claimId}`);
  const body = encodeURIComponent(
    `Claim: ${claimId}\n\nQuote: "${quote}"\n\nWhat is wrong or missing:\n\nEvidence (links):\n`,
  );
  return `https://github.com/${repo}/issues/new?labels=correction&title=${title}&body=${body}`;
}

export function explorerUrl(kind: string, ref: string, network: string): string | null {
  const net = network === 'pubnet' ? 'public' : 'testnet';
  if (kind === 'soroban_contract') return `https://stellar.expert/explorer/${net}/contract/${ref}`;
  if (kind === 'asset_issuer') return `https://stellar.expert/explorer/${net}/asset/${ref}`;
  if (kind === 'anchor') return `https://${ref}/.well-known/stellar.toml`;
  return null;
}

export function formatDateTime(iso: string): string {
  return `${new Date(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
  })} UTC`;
}
