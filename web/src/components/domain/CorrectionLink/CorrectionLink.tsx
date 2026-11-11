import { correctionUrl } from '@/lib/format';
import { ExternalLink } from '../../ui/ExternalLink';

export interface CorrectionLinkProps {
  repo: string;
  claimId: string;
  quote: string;
}

export function CorrectionLink({ repo, claimId, quote }: CorrectionLinkProps) {
  return (
    <ExternalLink href={correctionUrl(repo, claimId, quote)}>Suggest a correction</ExternalLink>
  );
}
