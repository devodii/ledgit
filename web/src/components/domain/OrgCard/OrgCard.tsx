import { Link } from '../../ui/Link';
import { OrgAvatar } from '../OrgAvatar';
import styles from './OrgCard.module.scss';

export interface OrgCardProps {
  slug: string;
  name: string;
  domain?: string;
  country?: string;
  claimCount: number;
}

export function OrgCard({ slug, name, domain, country, claimCount }: OrgCardProps) {
  return (
    <article className={styles.card}>
      <OrgAvatar name={name} size="lg" />
      <div className={styles.body}>
        <h3>
          <Link to={`/orgs/${slug}`}>{name}</Link>
        </h3>
        <p className={styles.meta}>
          {[domain, country].filter(Boolean).join(' · ') || 'No domain or country found'}
        </p>
      </div>
      <span className={styles.count}>
        {claimCount} claim{claimCount === 1 ? '' : 's'}
      </span>
    </article>
  );
}
