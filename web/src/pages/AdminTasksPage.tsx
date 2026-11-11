import { useEffect, useRef } from 'react';
import { useAdminTasks } from '@/api/hooks';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import styles from './pages.module.scss';

function beep() {
  try {
    const context = new AudioContext();
    const oscillator = context.createOscillator();
    oscillator.frequency.value = 880;
    oscillator.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 0.2);
  } catch {
    return;
  }
}

export function AdminTasksPage() {
  const tasks = useAdminTasks();
  const previous = useRef<number | null>(null);
  const open = tasks.data?.open_count ?? null;
  useEffect(() => {
    if (open !== null && previous.current !== null && open > previous.current) beep();
    if (open !== null) previous.current = open;
  }, [open]);

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1>Needs you ({open ?? '…'})</h1>
        <p>
          Open human tasks from the pipeline. A sound plays when a new one arrives while this tab is
          open.
        </p>
      </section>
      {tasks.isError && (
        <ErrorState
          title="Admin tasks are not available"
          description="This page only works when the API runs with ENV=local."
          onRetry={() => tasks.refetch()}
        />
      )}
      {tasks.data && tasks.data.tasks.length === 0 && (
        <EmptyState icon="check-circle" title="Nothing needs you" />
      )}
      <div className={styles.orgGrid}>
        {tasks.data?.tasks.map((task) => (
          <Card key={task.id}>
            <h3>
              #{task.id} {task.kind}
            </h3>
            <p>{task.description}</p>
            {task.url && <p className="mono">{task.url}</p>}
            <p>{task.resume_hint}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
