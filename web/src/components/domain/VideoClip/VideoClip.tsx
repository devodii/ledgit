import { useState } from 'react';
import { Icon } from '../../ui/Icon';
import styles from './VideoClip.module.scss';

export interface VideoClipProps {
  videoId: string;
  startSeconds: number;
  title: string;
}

function formatTime(total: number): string {
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

export function VideoClip({ videoId, startSeconds, title }: VideoClipProps) {
  const [loaded, setLoaded] = useState(false);
  const watchUrl = `https://www.youtube.com/watch?v=${videoId}&t=${startSeconds}s`;

  return (
    <div className={styles.clip}>
      {loaded ? (
        <iframe
          className={styles.frame}
          src={`https://www.youtube-nocookie.com/embed/${videoId}?start=${startSeconds}&autoplay=1&rel=0`}
          title={title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
          referrerPolicy="strict-origin-when-cross-origin"
        />
      ) : (
        <button
          type="button"
          className={styles.poster}
          onClick={() => setLoaded(true)}
          aria-label={`Play the clip from ${formatTime(startSeconds)}: ${title}`}
        >
          <img
            src={`https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`}
            alt=""
            loading="lazy"
            className={styles.image}
          />
          <span className={styles.play}>
            <Icon name="play" size="lg" />
          </span>
          <span className={styles.time}>Starts at {formatTime(startSeconds)}</span>
        </button>
      )}
      <a className={styles.link} href={watchUrl} target="_blank" rel="noopener noreferrer">
        Open on YouTube at {formatTime(startSeconds)}
        <Icon name="external" size="sm" />
      </a>
    </div>
  );
}
