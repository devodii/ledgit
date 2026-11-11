import { Icon } from '../../ui/Icon';
import styles from './SpeakerByline.module.scss';

export interface SpeakerBylineProps {
  name?: string;
  role?: string;
  org?: string;
}

export function SpeakerByline({ name, role, org }: SpeakerBylineProps) {
  const detail = [role, org].filter(Boolean).join(' at ');
  return (
    <p className={styles.byline}>
      <Icon name="user" size="sm" />
      <span>
        <strong>{name || 'Speaker not stated in the talk'}</strong>
        {detail && <span className={styles.detail}>{detail}</span>}
      </span>
    </p>
  );
}
