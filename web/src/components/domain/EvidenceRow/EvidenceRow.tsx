import type { ClaimDetailData } from '@/api/client';
import { explorerUrl, timeAgo } from '@/lib/format';
import { Icon, type IconName } from '../../ui/Icon';
import { AddressPill } from '../AddressPill';
import styles from './EvidenceRow.module.scss';

type Evidence = ClaimDetailData['evidence'][number];

const KIND: Record<Evidence['kind'], string> = {
  asset_issuer: 'Asset issuer',
  soroban_contract: 'Soroban contract',
  anchor: 'Anchor',
  protocol_upgrade: 'Protocol upgrade',
};

const RESULT: Record<string, { label: string; icon: IconName; tone: string }> = {
  live: { label: 'Found live', icon: 'check-circle', tone: 'live' },
  testnet_only: { label: 'Testnet only', icon: 'flask', tone: 'testnet' },
  inactive: { label: 'Present, activity unconfirmed', icon: 'hourglass', tone: 'pending' },
  not_found: { label: 'Nothing found', icon: 'circle-dashed', tone: 'nothing' },
  error: { label: 'Check could not run', icon: 'alert', tone: 'error' },
};

export interface EvidenceRowProps {
  evidence: Evidence;
}

export function EvidenceRow({ evidence }: EvidenceRowProps) {
  const observation = evidence.latest_observation;
  const result = observation ? RESULT[observation.result] : null;
  const summary =
    observation && typeof observation.detail.summary === 'string' ? observation.detail.summary : '';
  const isAddress = evidence.kind !== 'protocol_upgrade' && evidence.kind !== 'anchor';
  return (
    <li className={styles.row}>
      <div className={styles.head}>
        <span className={styles.kind}>{KIND[evidence.kind]}</span>
        {result ? (
          <span className={`${styles.result} ${styles[result.tone]}`}>
            <Icon name={result.icon} size="sm" />
            {result.label}
          </span>
        ) : (
          <span className={`${styles.result} ${styles.nothing}`}>
            <Icon name="hourglass" size="sm" />
            Not checked yet
          </span>
        )}
      </div>
      {isAddress ? (
        <AddressPill
          value={evidence.ref}
          network={evidence.network}
          href={explorerUrl(evidence.kind, evidence.ref, evidence.network)}
        />
      ) : (
        <code className={styles.ref}>{evidence.ref}</code>
      )}
      {summary && <p className={styles.summary}>{summary}</p>}
      <p className={styles.meta}>
        Found via {evidence.found_via}
        {observation && <span> · Checked {timeAgo(observation.checked_at)}</span>}
      </p>
    </li>
  );
}
