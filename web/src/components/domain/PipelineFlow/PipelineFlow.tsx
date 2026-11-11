import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useMemo, useState } from 'react';
import { CONNECTORS, type ConnectorHealth, type ConnectorInfo } from '@/fixtures/connectors';
import { Icon, type IconName } from '../../ui/Icon';
import { ConnectorCard } from '../ConnectorCard';
import styles from './PipelineFlow.module.scss';

type SourceData = { connector: ConnectorInfo; health: ConnectorHealth };
type StageData = { label: string; detail: string };
type OutputData = { label: string; detail: string };
type SourceNodeT = Node<SourceData, 'source'>;
type StageNodeT = Node<StageData, 'stage'>;
type OutputNodeT = Node<OutputData, 'output'>;

const HEALTH_ICON: Record<ConnectorHealth, IconName> = {
  ok: 'check-circle',
  down: 'alert',
  needs_human: 'hand',
  checking: 'hourglass',
};
const HEALTH_LABEL: Record<ConnectorHealth, string> = {
  ok: 'Healthy',
  down: 'Not responding',
  needs_human: 'Needs you',
  checking: 'Checking',
};

function SourceNode({ data, selected }: NodeProps<SourceNodeT>) {
  const { connector, health } = data;
  return (
    <div
      className={`${styles.node} ${styles.source} ${selected ? styles.selected : ''}`}
      aria-label={`${connector.name}, ${connector.role} source, ${HEALTH_LABEL[health]}`}
    >
      <span className={styles.title}>{connector.name}</span>
      <span className={`${styles.pill} ${styles[health]}`}>
        <Icon name={HEALTH_ICON[health]} size="sm" />
        {HEALTH_LABEL[health]}
      </span>
      <span className={styles.meta}>{connector.role === 'primary' ? 'Primary' : 'Secondary'}</span>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

function StageNode({ data, selected }: NodeProps<StageNodeT>) {
  return (
    <div className={`${styles.node} ${styles.stage} ${selected ? styles.selected : ''}`}>
      <Handle type="target" position={Position.Left} />
      <span className={styles.title}>{data.label}</span>
      <span className={styles.meta}>{data.detail}</span>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

function OutputNode({ data, selected }: NodeProps<OutputNodeT>) {
  return (
    <div className={`${styles.node} ${styles.output} ${selected ? styles.selected : ''}`}>
      <Handle type="target" position={Position.Left} />
      <span className={styles.title}>{data.label}</span>
      <span className={styles.meta}>{data.detail}</span>
    </div>
  );
}

const nodeTypes = { source: SourceNode, stage: StageNode, output: OutputNode };

const STAGES: StageData[] = [
  { label: 'Discover', detail: 'Playlists, title and date gates' },
  { label: 'Transcripts', detail: 'Timed captions, manual or auto' },
  { label: 'Extract', detail: 'LLM claims, verbatim quote check' },
  { label: 'Rank', detail: 'Score, dedupe, cap per talk' },
  { label: 'Resolve', detail: 'Org, domain, addresses, sources' },
  { label: 'Write registry', detail: 'YAML with provenance' },
  { label: 'Verify', detail: 'Daily checks, computed verdict' },
];

const OUTPUTS: OutputData[] = [
  { label: 'Registry YAML', detail: 'data/registry, data/review' },
  { label: 'Database', detail: 'Claims, observations, history' },
  { label: 'Public verdict', detail: 'Computed, never typed' },
];

const FEEDS: Record<string, string[]> = {
  youtube: ['stage-0'],
  transcripts: ['stage-1'],
  sessions: ['stage-2'],
  stellar_toml: ['stage-4', 'stage-6'],
  stellar_expert: ['stage-4'],
  scf: ['stage-4'],
  browser: ['stage-4'],
  lumenloop: ['stage-4'],
  stellarlight: ['stage-4'],
  sep_info: ['stage-6'],
  horizon: ['stage-6'],
  soroban: ['stage-6'],
};

const ROW = 84;
const STAGE_ROW = (CONNECTORS.length * ROW) / STAGES.length;

function buildGraph(health: Record<string, ConnectorHealth>) {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  CONNECTORS.forEach((connector, index) => {
    nodes.push({
      id: `source-${connector.name}`,
      type: 'source',
      position: { x: 0, y: index * ROW },
      data: { connector, health: health[connector.name] ?? 'ok' },
      sourcePosition: Position.Right,
    });
    for (const target of FEEDS[connector.name] ?? []) {
      const secondary = connector.role === 'secondary' || connector.name === 'browser';
      edges.push({
        id: `e-${connector.name}-${target}`,
        source: `source-${connector.name}`,
        target,
        animated: health[connector.name] === 'checking',
        style: secondary ? { strokeDasharray: '6 4' } : undefined,
        markerEnd: { type: MarkerType.ArrowClosed },
      });
    }
  });
  STAGES.forEach((stage, index) => {
    nodes.push({
      id: `stage-${index}`,
      type: 'stage',
      position: { x: 420, y: index * STAGE_ROW + 8 },
      data: stage,
    });
    if (index > 0) {
      edges.push({
        id: `e-stage-${index - 1}-${index}`,
        source: `stage-${index - 1}`,
        target: `stage-${index}`,
        markerEnd: { type: MarkerType.ArrowClosed },
        className: styles.mainEdge,
      });
    }
  });
  const outputY = [STAGE_ROW * 5 - 20, STAGE_ROW * 5 + 60, STAGE_ROW * 6 + 20];
  OUTPUTS.forEach((output, index) => {
    nodes.push({
      id: `output-${index}`,
      type: 'output',
      position: { x: 820, y: outputY[index] },
      data: output,
    });
  });
  const link = (id: string, source: string, target: string) =>
    edges.push({ id, source, target, markerEnd: { type: MarkerType.ArrowClosed } });
  link('e-write-registry', 'stage-5', 'output-0');
  link('e-write-db', 'stage-5', 'output-1');
  link('e-verify-verdict', 'stage-6', 'output-2');
  return { nodes, edges };
}

export interface PipelineFlowProps {
  health?: Record<string, ConnectorHealth>;
  height?: number;
}

export function PipelineFlow({ health = {}, height = 760 }: PipelineFlowProps) {
  const { nodes, edges } = useMemo(() => buildGraph(health), [health]);
  const [selected, setSelected] = useState<string | null>(null);
  const connector = CONNECTORS.find((c) => c.name === selected);

  return (
    <section className={styles.wrapper} aria-label="Data pipeline flow">
      <div className={styles.canvas} style={{ height }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          colorMode="dark"
          fitView
          fitViewOptions={{ padding: 0.12 }}
          nodesDraggable={false}
          nodesConnectable={false}
          minZoom={0.3}
          proOptions={{ hideAttribution: true }}
          onSelectionChange={({ nodes: picked }) => {
            const first = picked[0];
            setSelected(first?.id.startsWith('source-') ? first.id.replace('source-', '') : null);
          }}
        >
          <Background gap={24} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <p className={styles.legend}>
        Solid lines are primary sources. Dashed lines are secondary or fallback sources. Select a
        connector to see its details.
      </p>
      {connector && (
        <ConnectorCard
          connector={connector}
          health={health[connector.name] ?? 'ok'}
          lastChecked="just now"
        />
      )}
    </section>
  );
}
