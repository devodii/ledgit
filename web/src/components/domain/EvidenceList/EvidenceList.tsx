import type { ClaimDetailData } from '@/api/client';
import { EmptyState } from '../../ui/EmptyState';
import { EvidenceRow } from '../EvidenceRow';
import styles from './EvidenceList.module.scss';

export interface EvidenceListProps {
  evidence: ClaimDetailData['evidence'];
}

export function EvidenceList({ evidence }: EvidenceListProps) {
  if (evidence.length === 0) {
    return (
      <EmptyState
        icon="circle-dashed"
        title="No evidence linked yet"
        description="We could not link this organisation to any address, contract, anchor or protocol release with a public source."
      />
    );
  }
  return (
    <ul className={styles.list}>
      {evidence.map((item) => (
        <EvidenceRow key={item.id} evidence={item} />
      ))}
    </ul>
  );
}
