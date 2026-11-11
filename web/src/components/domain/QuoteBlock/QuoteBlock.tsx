import styles from './QuoteBlock.module.scss';

export interface QuoteBlockProps {
  quote: string;
  speaker?: string;
  role?: string;
  captionSource?: 'manual' | 'auto';
}

export function QuoteBlock({ quote, speaker, role, captionSource }: QuoteBlockProps) {
  return (
    <figure className={styles.figure}>
      <blockquote className={styles.quote}>{quote}</blockquote>
      <figcaption className={styles.caption}>
        <span>
          {speaker ? `${speaker}${role ? `, ${role}` : ''}` : 'Speaker not stated in the talk'}
        </span>
        {captionSource === 'auto' && (
          <span className={styles.note}>
            Quoted from automatic captions, which can contain errors.
          </span>
        )}
      </figcaption>
    </figure>
  );
}
