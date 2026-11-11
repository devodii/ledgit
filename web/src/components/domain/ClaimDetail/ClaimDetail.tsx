import type { ClaimDetailData } from '@/api/client';
import { GITHUB_REPO } from '@/api/client';
import { chainFromClaim } from '@/lib/chain';
import { Icon } from '../../ui/Icon';
import { Link } from '../../ui/Link';
import { Tabs } from '../../ui/Tabs';
import { BackingRow } from '../BackingRow';
import { CorrectionLink } from '../CorrectionLink';
import { EvidenceChain } from '../EvidenceChain';
import { EvidenceList } from '../EvidenceList';
import { MethodologyCallout } from '../MethodologyCallout';
import { OrgAvatar } from '../OrgAvatar';
import { QuoteBlock } from '../QuoteBlock';
import { SpeakerByline } from '../SpeakerByline';
import { VerdictBanner } from '../VerdictBanner';
import { VerdictTimeline } from '../VerdictTimeline';
import { VideoClip } from '../VideoClip';
import styles from './ClaimDetail.module.scss';

export interface ClaimDetailProps {
  claim: ClaimDetailData;
}

export function ClaimDetail({ claim }: ClaimDetailProps) {
  return (
    <article className={styles.page}>
      <header className={styles.header}>
        <OrgAvatar name={claim.org.name} size="lg" />
        <div>
          <h1>
            <Link to={`/orgs/${claim.org.slug}`}>{claim.org.name}</Link>
          </h1>
          <p className={styles.meta}>
            {[claim.org.domain, claim.org.country].filter(Boolean).join(' · ') ||
              'No domain or country found'}
          </p>
        </div>
      </header>

      <VerdictBanner
        status={claim.verdict.status}
        reason={claim.verdict.reason}
        checkedAt={claim.verdict.checked_at}
      />

      <div className={styles.split}>
        <div className={styles.column}>
          <VideoClip
            videoId={claim.video.id}
            startSeconds={claim.video.start_seconds}
            title={`${claim.org.name} at ${claim.event}`}
          />
          <QuoteBlock
            quote={claim.quote}
            speaker={claim.speaker_name}
            role={claim.speaker_role}
            captionSource={claim.video.caption_source}
          />
          <SpeakerByline name={claim.speaker_name} role={claim.speaker_role} org={claim.org.name} />
          <p className={styles.summary}>
            <Icon name="info" size="sm" /> {claim.summary}
          </p>
          <BackingRow
            found={claim.scf.found}
            projectUrl={claim.scf.project_url}
            awardedUsd={claim.scf.awarded_usd}
            source={claim.scf_source}
          />
        </div>
        <div className={styles.column}>
          <EvidenceChain chain={chainFromClaim(claim)} />
        </div>
      </div>

      <Tabs
        tabs={[
          {
            value: 'evidence',
            label: `Evidence (${claim.evidence.length})`,
            content: <EvidenceList evidence={claim.evidence} />,
          },
          {
            value: 'history',
            label: 'Verdict history',
            content: <VerdictTimeline history={claim.history} />,
          },
          {
            value: 'sources',
            label: 'Where this came from',
            content: (
              <ul className={styles.sources}>
                {claim.domain_source && <li>Domain: {claim.domain_source}</li>}
                {claim.country_source && <li>Country: {claim.country_source}</li>}
                {claim.scf_source && <li>SCF: {claim.scf_source}</li>}
                {claim.sources.map((source) => (
                  <li key={`${source.name}-${source.url}`}>
                    <strong>{source.name}</strong> provided {source.provides.join(', ')}:{' '}
                    <a href={source.url} target="_blank" rel="noopener noreferrer">
                      {source.url}
                    </a>
                  </li>
                ))}
                <li>
                  Extracted with {claim.extractor_model}, confidence {claim.confidence.toFixed(2)}.
                </li>
              </ul>
            ),
          },
        ]}
      />

      <footer className={styles.footer}>
        <CorrectionLink repo={GITHUB_REPO} claimId={claim.id} quote={claim.quote} />
        <MethodologyCallout />
      </footer>
    </article>
  );
}
