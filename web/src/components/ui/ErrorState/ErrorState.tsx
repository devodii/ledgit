import { Button } from '../Button';
import { Icon } from '../Icon';
import styles from './ErrorState.module.scss';

export interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Something went wrong',
  description = 'We could not load this. Please try again.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className={styles.error} role="alert">
      <Icon name="alert" size="lg" />
      <h3>{title}</h3>
      <p>{description}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
