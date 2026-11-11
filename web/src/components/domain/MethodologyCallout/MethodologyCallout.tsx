import { Icon } from '../../ui/Icon';
import { Link } from '../../ui/Link';
import styles from './MethodologyCallout.module.scss';

export function MethodologyCallout() {
  return (
    <aside className={styles.callout}>
      <Icon name="info" size="md" />
      <p>
        Quotes are exact text from the talk captions. Verdicts are computed from public on-chain
        data and never typed by a person. <Link to="/methodology">How it works and its limits</Link>
      </p>
    </aside>
  );
}
