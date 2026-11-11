import { formatUsd } from '@/lib/format';
import { ExternalLink } from '../../ui/ExternalLink';
import { Icon } from '../../ui/Icon';
import styles from './BackingRow.module.scss';

export interface BackingRowProps {
  found: boolean;
  projectUrl?: string;
  awardedUsd?: number | string | null;
  source?: string;
}

export function BackingRow({ found, projectUrl, awardedUsd, source }: BackingRowProps) {
  if (!found) return null;
  return (
    <div className={styles.row}>
      <Icon name="award" size="md" />
      <div>
        <p className={styles.title}>
          Stellar Community Fund award
          {awardedUsd ? <span className="mono"> {formatUsd(awardedUsd)}</span> : null}
        </p>
        <p className={styles.meta}>
          {projectUrl && <ExternalLink href={projectUrl}>Project page</ExternalLink>}
          {source && <span> Source: {source}</span>}
        </p>
      </div>
    </div>
  );
}
