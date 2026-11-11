import { Icon } from '../../ui/Icon';
import { QuoteBlock } from '../QuoteBlock';
import { StatusBadge, type VerdictStatus } from '../StatusBadge';
import { VideoClip } from '../VideoClip';
import styles from './ClaimCard.module.scss';

export interface ClaimCardProps {
  id: string;
  status: VerdictStatus;
  quote: string;
  speaker?: string;
  role?: string;
  orgName: string;
  videoId: string;
  videoTitle: string;
  startSeconds: number;
  captionSource: 'manual' | 'auto';
  lastChecked?: string;
  scfAwardedUsd?: number | null;
  href?: string;
}

export function ClaimCard(props: ClaimCardProps) {
  return (
    <article className={styles.card} aria-label={`Claim by ${props.orgName}`}>
      <header className={styles.header}>
        <h3 className={styles.org}>{props.orgName}</h3>
        <StatusBadge status={props.status} />
      </header>
      <VideoClip
        videoId={props.videoId}
        startSeconds={props.startSeconds}
        title={props.videoTitle}
      />
      <QuoteBlock
        quote={props.quote}
        speaker={props.speaker}
        role={props.role}
        captionSource={props.captionSource}
      />
      <footer className={styles.footer}>
        {props.scfAwardedUsd ? (
          <span className={styles.backing}>
            <Icon name="award" size="sm" />
            SCF awarded ${props.scfAwardedUsd.toLocaleString()}
          </span>
        ) : null}
        {props.lastChecked && <span>Last checked {props.lastChecked}</span>}
        {props.href && (
          <a className={styles.more} href={props.href}>
            See the evidence
            <Icon name="chevron-right" size="sm" />
          </a>
        )}
      </footer>
    </article>
  );
}
