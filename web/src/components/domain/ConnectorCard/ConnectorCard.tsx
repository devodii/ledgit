import type { ConnectorHealth, ConnectorInfo } from '@/fixtures/connectors';
import { Icon, type IconName } from '../../ui/Icon';
import styles from './ConnectorCard.module.scss';

export interface ConnectorCardProps {
  connector: ConnectorInfo;
  health: ConnectorHealth;
  detail?: string;
  lastChecked?: string;
}

const HEALTH: Record<ConnectorHealth, { label: string; icon: IconName }> = {
  ok: { label: 'Healthy', icon: 'check-circle' },
  down: { label: 'Not responding', icon: 'alert' },
  needs_human: { label: 'Needs you', icon: 'hand' },
  checking: { label: 'Checking', icon: 'hourglass' },
};

export function ConnectorCard({ connector, health, detail, lastChecked }: ConnectorCardProps) {
  const state = HEALTH[health];
  return (
    <article className={styles.card} aria-label={`${connector.name} connector`}>
      <header className={styles.header}>
        <h3 className={styles.name}>{connector.name}</h3>
        <span className={`${styles.health} ${styles[health]}`}>
          <Icon name={state.icon} size="sm" />
          {state.label}
        </span>
      </header>
      <p className={styles.summary}>{connector.summary}</p>
      {detail && <p className={styles.detail}>{detail}</p>}
      <dl className={styles.facts}>
        <div>
          <dt>Source</dt>
          <dd>{connector.role === 'primary' ? 'Primary' : 'Secondary'}</dd>
        </div>
        <div>
          <dt>Rate limit</dt>
          <dd className="mono">{connector.rateLimitRps} req/s</dd>
        </div>
        <div>
          <dt>Emits</dt>
          <dd className="mono">{connector.emits.join(', ')}</dd>
        </div>
        <div>
          <dt>Allowed domains</dt>
          <dd className="mono">{connector.allowedDomains.join(', ')}</dd>
        </div>
      </dl>
      {lastChecked && <p className={styles.checked}>Last checked {lastChecked}</p>}
    </article>
  );
}
