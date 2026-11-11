import { Icon, type IconName } from '../../ui/Icon';
import styles from './StatusBadge.module.scss';

export type VerdictStatus = 'live' | 'testnet_only' | 'no_trace_found' | 'pending' | 'open_ask';

export const STATUS_COPY: Record<VerdictStatus, { label: string; icon: IconName }> = {
  live: { label: 'Found live on Stellar mainnet', icon: 'check-circle' },
  testnet_only: { label: 'Found on testnet, not yet on mainnet', icon: 'flask' },
  no_trace_found: { label: 'We found no on-chain trace yet', icon: 'circle-dashed' },
  pending: { label: 'Too recent to assess', icon: 'hourglass' },
  open_ask: { label: 'Requested on stage, no builder identified', icon: 'hand' },
};

export interface StatusBadgeProps {
  status: VerdictStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const { label, icon } = STATUS_COPY[status];
  return (
    <span className={`${styles.badge} ${styles[status]}`}>
      <Icon name={icon} size="sm" />
      {label}
    </span>
  );
}
