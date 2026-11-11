import styles from './Spinner.module.scss';

export interface SpinnerProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Spinner({ label = 'Loading', size = 'md' }: SpinnerProps) {
  return <span className={`${styles.spinner} ${styles[size]}`} role="status" aria-label={label} />;
}
