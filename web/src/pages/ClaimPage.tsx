import { useParams } from 'react-router-dom';
import { useClaim } from '@/api/hooks';
import { ClaimDetail } from '@/components/domain/ClaimDetail';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { NotFoundPage } from './NotFoundPage';

export function ClaimPage() {
  const { id = '' } = useParams();
  const claim = useClaim(id);
  if (claim.isPending) return <Skeleton height="40rem" />;
  if (claim.isError) {
    return String(claim.error.message).includes('404') ? (
      <NotFoundPage />
    ) : (
      <ErrorState onRetry={() => claim.refetch()} />
    );
  }
  return <ClaimDetail claim={claim.data} />;
}
