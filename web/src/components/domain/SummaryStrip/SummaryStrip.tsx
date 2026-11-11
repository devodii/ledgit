import type { EventSummaryData } from '@/api/client';
import { Card } from '../../ui/Card';
import { Stat } from '../../ui/Stat';
import { STATUS_COPY } from '../StatusBadge';
import styles from './SummaryStrip.module.scss';

export interface SummaryStripProps {
  summary: EventSummaryData;
}

export function SummaryStrip({ summary }: SummaryStripProps) {
  return (
    <Card as="section" className={styles.strip}>
      <Stat label={`Claims from ${summary.name}`} value={summary.total} />
      {summary.by_status.map((row) => (
        <Stat key={row.status} label={STATUS_COPY[row.status].label} value={row.count} />
      ))}
    </Card>
  );
}
