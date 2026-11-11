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
import { useMemo } from 'react';
import { CONNECTORS, type ConnectorHealth, type ConnectorInfo } from '@/fixtures/connectors';
import { HoverCard } from '../../ui/HoverCard';
import { Icon, type IconName } from '../../ui/Icon';
import { ConnectorCard } from '../ConnectorCard';
import styles from './PipelineFlow.module.scss';

type SourceData = { connector: ConnectorInfo; health: ConnectorHealth };
type StageData = { index: number; label: string; detail: string; icon: IconName; feeds: string[] };
type OutputData = { label: string; detail: string; icon: IconName };
type SourceNodeT = Node<SourceData, 'source'>;
type StageNodeT = Node<StageData, 'stage'>;
type OutputNodeT = Node<OutputData, 'output'>;

const CONNECTOR_ICON: Record<string, IconName> = {
  youtube: 'video',
  transcripts: 'message',
  sessions: 'user',
  stellar_toml: 'file',
  sep_info: 'server',
  horizon: 'layers',
  soroban: 'code',
  stellar_expert: 'search',
  scf: 'award',
  browser: 'globe',
  lumenloop: 'link',
  stellarlight: 'filter',
};

const HEALTH_ICON: Record<ConnectorHealth, IconName> = {
  ok: 'check-circle',
  down: 'alert',
  needs_human: 'hand',
  checking: 'hourglass',
};

function SourceNode({ data }: NodeProps<SourceNodeT>) {
  const { connector, health } = data;
  return (
    <HoverCard
      side="right"
      content={<ConnectorCard connector={connector} health={health} lastChecked="just now" />}
    >
      <div
        className={styles.orb}
        tabIndex={0}
        role="group"
        aria-label={`${connector.name} connector, ${connector.role}, ${health}`}
      >
        <span
          className={`${styles.circle} ${styles[health]} ${connector.role === 'secondary' ? styles.secondary : ''}`}
        >
          <Icon name={CONNECTOR_ICON[connector.name] ?? 'link'} size="lg" />
          <span className={`${styles.badge} ${styles[health]}`}>
            <Icon name={HEALTH_ICON[health]} size="sm" />
          </span>
        </span>
        <span className={styles.label}>{connector.name}</span>
        <Handle type="source" position={Position.Right} />
      </div>
    </HoverCard>
  );
}

function StageNode({ data }: NodeProps<StageNodeT>) {
  return (
    <HoverCard
      side="top"
      content={
        <div className={styles.info}>
          <h3>
            {data.index + 1}. {data.label}
          </h3>
          <p>{data.detail}</p>
          {data.feeds.length > 0 && (
            <p className={styles.feeds}>
              Fed by <span className="mono">{data.feeds.join(', ')}</span>
            </p>
          )}
        </div>
      }
    >
      <div
        className={styles.stage}
        tabIndex={0}
        role="group"
        aria-label={`Stage ${data.index + 1}, ${data.label}`}
      >
        <Handle type="target" position={Position.Left} />
        <span className={styles.step}>{data.index + 1}</span>
        <Icon name={data.icon} size="sm" />
        <span>{data.label}</span>
        <Handle type="source" position={Position.Right} />
      </div>
    </HoverCard>
  );
}

function OutputNode({ data }: NodeProps<OutputNodeT>) {
  return (
    <HoverCard
      side="left"
      content={
        <div className={styles.info}>
          <h3>{data.label}</h3>
          <p>{data.detail}</p>
        </div>
      }
    >
      <div className={styles.orb} tabIndex={0} role="group" aria-label={data.label}>
        <Handle type="target" position={Position.Left} />
        <span className={`${styles.square}`}>
          <Icon name={data.icon} size="lg" />
        </span>
        <span className={styles.label}>{data.label}</span>
      </div>
    </HoverCard>
  );
}

const nodeTypes = { source: SourceNode, stage: StageNode, output: OutputNode };

const STAGES: Omit<StageData, 'index' | 'feeds'>[] = [
  {
    label: 'Discover',
    detail: 'Lists playlist videos and applies the title and date gates.',
    icon: 'search',
  },
  {
    label: 'Transcripts',
    detail: 'Fetches timed captions and records manual or auto.',
    icon: 'message',
  },
  {
    label: 'Extract',
    detail: 'The LLM proposes claims. Every quote must be a verbatim substring.',
    icon: 'filter',
  },
  {
    label: 'Rank',
    detail: 'Scores specificity and verifiability, removes duplicates, caps per talk.',
    icon: 'layers',
  },
  {
    label: 'Resolve',
    detail: 'Links each organisation to a domain, addresses and SCF, with a source for each.',
    icon: 'link',
  },
  {
    label: 'Write registry',
    detail: 'Writes the YAML with provenance and loads it into the database.',
    icon: 'file',
  },
  {
    label: 'Verify',
    detail: 'Checks every evidence item and computes the verdict.',
    icon: 'shield',
  },
];

const OUTPUTS: OutputData[] = [
  {
    label: 'Registry YAML',
    detail: 'data/registry and data/review, generated and committed.',
    icon: 'file',
  },
  { label: 'Database', detail: 'Claims, observations and verdict history.', icon: 'database' },
  {
    label: 'Public verdict',
    detail: 'Computed by code from the observations, never typed by hand.',
    icon: 'check-circle',
  },
];

const FEEDS: Record<string, number[]> = {
  youtube: [0],
  transcripts: [1],
  sessions: [2],
  stellar_toml: [4, 6],
  stellar_expert: [4],
  scf: [4],
  browser: [4],
  lumenloop: [4],
  stellarlight: [4],
  sep_info: [6],
  horizon: [6],
  soroban: [6],
};

const ROW = 92;
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
    });
    for (const stage of FEEDS[connector.name] ?? []) {
      const dashed = connector.role === 'secondary' || connector.name === 'browser';
      edges.push({
        id: `e-${connector.name}-${stage}`,
        source: `source-${connector.name}`,
        target: `stage-${stage}`,
        animated: health[connector.name] === 'checking',
        className: dashed ? styles.dashedEdge : styles.edge,
        markerEnd: { type: MarkerType.ArrowClosed },
      });
    }
  });
  STAGES.forEach((stage, index) => {
    const feeds = CONNECTORS.filter((c) => FEEDS[c.name]?.includes(index)).map((c) => c.name);
    nodes.push({
      id: `stage-${index}`,
      type: 'stage',
      position: { x: 380, y: index * STAGE_ROW + 10 },
      data: { ...stage, index, feeds },
    });
    if (index > 0) {
      edges.push({
        id: `e-stage-${index - 1}-${index}`,
        source: `stage-${index - 1}`,
        target: `stage-${index}`,
        className: styles.mainEdge,
        markerEnd: { type: MarkerType.ArrowClosed },
      });
    }
  });
  const outputY = [STAGE_ROW * 4.6, STAGE_ROW * 5.6, STAGE_ROW * 6.4];
  OUTPUTS.forEach((output, index) => {
    nodes.push({
      id: `output-${index}`,
      type: 'output',
      position: { x: 740, y: outputY[index] },
      data: output,
    });
  });
  const link = (id: string, source: string, target: string) =>
    edges.push({
      id,
      source,
      target,
      className: styles.edge,
      markerEnd: { type: MarkerType.ArrowClosed },
    });
  link('e-write-registry', 'stage-5', 'output-0');
  link('e-write-db', 'stage-5', 'output-1');
  link('e-verify-verdict', 'stage-6', 'output-2');
  return { nodes, edges };
}

export interface PipelineFlowProps {
  health?: Record<string, ConnectorHealth>;
  height?: number;
}

export function PipelineFlow({ health = {}, height = 780 }: PipelineFlowProps) {
  const { nodes, edges } = useMemo(() => buildGraph(health), [health]);
  return (
    <section className={styles.wrapper} aria-label="Data pipeline flow">
      <div className={styles.canvas} style={{ height }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          colorMode="dark"
          fitView
          fitViewOptions={{ padding: 0.1 }}
          nodesDraggable={false}
          nodesConnectable={false}
          nodesFocusable={false}
          elementsSelectable={false}
          minZoom={0.3}
          proOptions={{ hideAttribution: true }}
        >
          <Background gap={28} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <p className={styles.legend}>
        Solid lines are primary sources. Dashed lines are secondary or fallback sources. Hover or
        focus any node for details.
      </p>
    </section>
  );
}
