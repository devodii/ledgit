import { GITHUB_REPO } from '@/api/client';
import { ExternalLink } from '../../ui/ExternalLink';
import { Link } from '../../ui/Link';
import { LastUpdated } from '../../domain/LastUpdated';
import styles from './Footer.module.scss';

export interface FooterProps {
  lastVerifiedAt?: string | null;
  dataVersion?: string;
}

export function Footer({ lastVerifiedAt, dataVersion }: FooterProps) {
  return (
    <footer className={styles.footer}>
      <p>
        Ledgit reports what the Stellar network says about claims made on stage. It does not judge
        anyone. <Link to="/methodology">Methodology</Link>
      </p>
      <p className={styles.meta}>
        <LastUpdated iso={lastVerifiedAt} label="Last verification run" />
        {dataVersion && <span className="mono"> · data {dataVersion}</span>}
      </p>
      <p>
        <ExternalLink href={`https://github.com/${GITHUB_REPO}`}>
          Source and corrections on GitHub
        </ExternalLink>
      </p>
    </footer>
  );
}
