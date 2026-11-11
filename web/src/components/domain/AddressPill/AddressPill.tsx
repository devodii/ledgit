import { truncateMiddle } from '@/lib/format';
import { CopyButton } from '../../ui/CopyButton';
import { ExternalLink } from '../../ui/ExternalLink';
import styles from './AddressPill.module.scss';

export interface AddressPillProps {
  value: string;
  network: 'pubnet' | 'testnet';
  href?: string | null;
}

export function AddressPill({ value, network, href }: AddressPillProps) {
  return (
    <span className={styles.pill}>
      <span className={`${styles.network} ${styles[network]}`}>
        {network === 'pubnet' ? 'Mainnet' : 'Testnet'}
      </span>
      <code className={styles.value} title={value}>
        {truncateMiddle(value, 8, 6)}
      </code>
      <CopyButton value={value} label={`Copy ${value}`} />
      {href && <ExternalLink href={href}>Explorer</ExternalLink>}
    </span>
  );
}
