import { useParams } from 'react-router-dom';
import { useOrg } from '@/api/hooks';
import { OrgAvatar } from '@/components/domain/OrgAvatar';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { ClaimGrid } from './ClaimGrid';
import { NotFoundPage } from './NotFoundPage';
import styles from './pages.module.scss';

export function OrgPage() {
  const { slug = '' } = useParams();
  const org = useOrg(slug);
  if (org.isPending) return <Skeleton height="30rem" />;
  if (org.isError) {
    return String(org.error.message).includes('404') ? (
      <NotFoundPage />
    ) : (
      <ErrorState onRetry={() => org.refetch()} />
    );
  }
  const { org: details, claims } = org.data;
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <OrgAvatar name={details.name} size="lg" />
        <h1>{details.name}</h1>
        <p>
          {[details.domain, details.country].filter(Boolean).join(' · ') ||
            'No domain or country found'}
        </p>
      </section>
      <ClaimGrid claims={claims} />
    </div>
  );
}
