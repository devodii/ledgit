import type { ClaimSummary } from '@/api/client';
import { ClaimCard } from '@/components/domain/ClaimCard';
import styles from './pages.module.scss';

export function ClaimGrid({ claims }: { claims: ClaimSummary[] }) {
  return (
    <div className={styles.grid}>
      {claims.map((claim) => (
        <ClaimCard
          key={claim.id}
          id={claim.id}
          status={claim.status}
          quote={claim.quote}
          speaker={claim.speaker_name}
          role={claim.speaker_role}
          orgName={claim.org_name}
          videoId={claim.video_id}
          videoTitle={`${claim.org_name} at ${claim.event}`}
          startSeconds={claim.start_seconds}
          captionSource={claim.caption_source}
          lastChecked={claim.last_checked_at ? undefined : undefined}
          scfAwardedUsd={
            claim.scf_found && claim.scf_awarded_usd ? Number(claim.scf_awarded_usd) : null
          }
          href={`/claims/${claim.id}`}
        />
      ))}
    </div>
  );
}
