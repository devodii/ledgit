import styles from './QuoteBlock.module.scss';

export interface QuoteBlockProps {
  quote: string;
  speaker?: string;
  role?: string;
  captionSource?: 'manual' | 'auto';
}

const FILLER = /\b(uh|um|uhm|erm|er|ah)\b/gi;

function withQuietFillers(quote: string) {
  return quote.split(FILLER).map((part, index) =>
    index % 2 === 1 ? (
      <span key={index} className={styles.filler}>
        {part}
      </span>
    ) : (
      part
    ),
  );
}

export function QuoteBlock({ quote, speaker, role, captionSource }: QuoteBlockProps) {
  return (
    <figure className={styles.figure}>
      <blockquote className={styles.quote}>{withQuietFillers(quote)}</blockquote>
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
