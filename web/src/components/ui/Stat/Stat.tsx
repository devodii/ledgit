import styles from './Stat.module.scss';

export interface StatProps {
  label: string;
  value: string | number;
  delta?: string;
}

export function Stat({ label, value, delta }: StatProps) {
  return (
    <div className={styles.stat}>
      <span className={styles.label}>{label}</span>
      <span className={`${styles.value} mono`}>{value}</span>
      {delta && <span className={styles.delta}>{delta}</span>}
    </div>
  );
}
