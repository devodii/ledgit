import { EmptyState } from '@/components/ui/EmptyState';
import { Link } from '@/components/ui/Link';

export function NotFoundPage() {
  return (
    <EmptyState
      icon="circle-dashed"
      title="We could not find that page"
      description="The claim or organisation may have been removed or the link may be wrong."
      action={<Link to="/">Back to all claims</Link>}
    />
  );
}
