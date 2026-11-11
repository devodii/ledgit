import type { ClaimDetailData } from '@/api/client';
import type { ChainData, ChainEvidence } from '@/fixtures/evidenceChain';
import { timeAgo } from './format';

export function chainFromClaim(claim: ClaimDetailData): ChainData {
  const evidence: ChainEvidence[] = claim.evidence.map((item) => {
    const observation = item.latest_observation;
    const summary =
      observation && typeof observation.detail.summary === 'string'
        ? observation.detail.summary
        : '';
    return {
      id: `e${item.id}`,
      kind: item.kind,
      network: item.network,
      ref: item.ref,
      foundVia: item.found_via,
      result: observation && observation.result !== 'inactive' ? observation.result : null,
      detail:
        summary ||
        (observation?.result === 'inactive' ? 'Present, activity unconfirmed' : 'Not checked yet'),
      checkedAt: observation ? timeAgo(observation.checked_at) : 'never',
    };
  });
  return {
    claim: {
      quote: claim.quote,
      speaker: claim.speaker_name,
      role: claim.speaker_role,
      video: {
        id: claim.video.id,
        startSeconds: claim.video.start_seconds,
        title: `${claim.org.name} at ${claim.event}`,
      },
    },
    org: { name: claim.org.name, domain: claim.org.domain, country: claim.org.country },
    evidence,
    verdict: { status: claim.verdict.status, reason: claim.verdict.reason },
  };
}
