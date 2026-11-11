import {
  Background,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useEffect, useMemo, useRef, useState } from 'react';
import type { ChainData, ChainEvidence, ObservationResult } from '@/fixtures/evidenceChain';
import { Icon, type IconName } from '../../ui/Icon';
import { HoverCard } from '../../ui/HoverCard';
import styles from './EvidenceChain.module.scss';

type Kind = 'claim' | 'org' | 'evidence' | 'verdict';
type CardRow = [string, string];
type ChainNodeData = {
  kind: Kind;
  label: string;
  icon: IconName;
  tone: string;
  card: { heading: string; rows: CardRow[]; note?: string };
  vertical: boolean;
};
type ChainNode = Node<ChainNodeData, 'chain'>;

const RESULT_TONE: Record<ObservationResult | 'none', string> = {
  live: 'live',
  testnet_only: 'testnet',
  not_found: 'nothing',
  error: 'error',
  none: 'nothing',
};
const RESULT_LABEL: Record<ObservationResult | 'none', string> = {
  live: 'Found live',
  testnet_only: 'Testnet only',
  not_found: 'Nothing found',
  error: 'Check failed',
  none: 'Not checked',
};
const VERDICT_TONE: Record<ChainData['verdict']['status'], string> = {
  live: 'live',
  testnet_only: 'testnet',
  no_trace_found: 'nothing',
  pending: 'pending',
  open_ask: 'ask',
};
const VERDICT_LABEL: Record<ChainData['verdict']['status'], string> = {
  live: 'Found live on Stellar mainnet',
  testnet_only: 'Found on testnet, not yet on mainnet',
  no_trace_found: 'We found no on-chain trace yet',
  pending: 'Too recent to assess',
  open_ask: 'Requested on stage, no builder identified',
};
const VERDICT_ICON: Record<ChainData['verdict']['status'], IconName> = {
  live: 'check-circle',
  testnet_only: 'flask',
  no_trace_found: 'circle-dashed',
  pending: 'hourglass',
  open_ask: 'hand',
};
const KIND_LABEL: Record<ChainEvidence['kind'], string> = {
  asset_issuer: 'Asset issuer',
  soroban_contract: 'Soroban contract',
  anchor: 'Anchor',
  protocol_upgrade: 'Protocol upgrade',
};
const RESULT_ICON: Record<ObservationResult | 'none', IconName> = {
  live: 'check-circle',
  testnet_only: 'flask',
  not_found: 'circle-dashed',
  error: 'alert',
  none: 'hourglass',
};

function ChainNodeView({ data }: NodeProps<ChainNode>) {
  const target = data.vertical ? Position.Top : Position.Left;
  const source = data.vertical ? Position.Bottom : Position.Right;
  const big = data.kind === 'verdict';
  return (
    <HoverCard
      side={data.vertical ? 'right' : 'top'}
      content={
        <div className={styles.card}>
          <h3>{data.card.heading}</h3>
          <dl>
            {data.card.rows.map(([name, value]) => (
              <div key={name}>
                <dt>{name}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          {data.card.note && <p>{data.card.note}</p>}
        </div>
      }
    >
      <div
        className={styles.orb}
        tabIndex={0}
        role="group"
        aria-label={`${data.label}. ${data.card.heading}`}
      >
        {data.kind !== 'claim' && <Handle type="target" position={target} />}
        <span className={`${styles.circle} ${styles[data.tone]} ${big ? styles.big : ''}`}>
          <Icon name={data.icon} size="lg" />
        </span>
        <span className={styles.label}>{data.label}</span>
        {data.kind !== 'verdict' && <Handle type="source" position={source} />}
      </div>
    </HoverCard>
  );
}

const nodeTypes = { chain: ChainNodeView };
const NODE_W = 150;
const GAP_X = 120;
const GAP_Y = 36;

function layout(chain: ChainData, vertical: boolean) {
  const nodes: ChainNode[] = [];
  const edges: Edge[] = [];
  const base = { vertical };
  const place = (column: number, row: number, rows: number, tall: number) =>
    vertical
      ? {
          x:
            ((Math.max(chain.evidence.length, 1) - rows) * (NODE_W + 24)) / 2 + row * (NODE_W + 24),
          y: column * (tall + GAP_Y),
        }
      : {
          x: column * (NODE_W + GAP_X),
          y: row * (tall + GAP_Y) - ((rows - 1) * (tall + GAP_Y)) / 2,
        };

  nodes.push({
    id: 'claim',
    type: 'chain',
    position: place(0, 0, 1, 130),
    data: {
      ...base,
      kind: 'claim',
      label: 'Claim',
      icon: 'message',
      tone: 'neutral',
      card: {
        heading: `"${chain.claim.quote}"`,
        rows: [
          ['Speaker', chain.claim.speaker || 'Not stated'],
          ['Role', chain.claim.role || 'Not stated'],
        ],
      },
    },
  });
  nodes.push({
    id: 'org',
    type: 'chain',
    position: place(1, 0, 1, 130),
    data: {
      ...base,
      kind: 'org',
      label: chain.org.name,
      icon: 'link',
      tone: 'neutral',
      card: {
        heading: chain.org.name,
        rows: [
          ['Domain', chain.org.domain || 'Not found'],
          ['Country', chain.org.country || 'Not found'],
        ],
      },
    },
  });
  edges.push({
    id: 'claim-org',
    source: 'claim',
    target: 'org',
    markerEnd: { type: MarkerType.ArrowClosed },
  });

  const count = Math.max(chain.evidence.length, 1);
  chain.evidence.forEach((item, index) => {
    const tone = RESULT_TONE[item.result ?? 'none'];
    nodes.push({
      id: item.id,
      type: 'chain',
      position: place(2, index, count, 130),
      data: {
        ...base,
        kind: 'evidence',
        label: KIND_LABEL[item.kind],
        icon: RESULT_ICON[item.result ?? 'none'],
        tone,
        card: {
          heading: `${KIND_LABEL[item.kind]} on ${item.network}`,
          rows: [
            ['Reference', item.ref],
            ['Result', RESULT_LABEL[item.result ?? 'none']],
            ['What we saw', item.detail],
            ['Found via', item.foundVia],
            ['Last checked', item.checkedAt],
          ],
        },
      },
    });
    edges.push({
      id: `org-${item.id}`,
      source: 'org',
      target: item.id,
      label: RESULT_LABEL[item.result ?? 'none'],
      className: styles[`edge_${tone}`],
      markerEnd: { type: MarkerType.ArrowClosed },
      style:
        item.result === 'live'
          ? undefined
          : { strokeDasharray: item.result === 'testnet_only' ? '8 4' : '2 5' },
    });
    edges.push({
      id: `${item.id}-verdict`,
      source: item.id,
      target: 'verdict',
      className: styles[`edge_${tone}`],
      markerEnd: { type: MarkerType.ArrowClosed },
    });
  });
  if (chain.evidence.length === 0) {
    edges.push({
      id: 'org-verdict',
      source: 'org',
      target: 'verdict',
      markerEnd: { type: MarkerType.ArrowClosed },
    });
  }
  const status = chain.verdict.status;
  nodes.push({
    id: 'verdict',
    type: 'chain',
    position: place(chain.evidence.length ? 3 : 2, 0, 1, 130),
    data: {
      ...base,
      kind: 'verdict',
      label: VERDICT_LABEL[status],
      icon: VERDICT_ICON[status],
      tone: VERDICT_TONE[status],
      card: { heading: VERDICT_LABEL[status], rows: [], note: chain.verdict.reason },
    },
  });
  return { nodes, edges };
}

export interface EvidenceChainProps {
  chain: ChainData;
}

export function EvidenceChain({ chain }: EvidenceChainProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [vertical, setVertical] = useState(false);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setVertical(entry.contentRect.width < 720));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const { nodes, edges } = useMemo(() => layout(chain, vertical), [chain, vertical]);
  const height = vertical
    ? 480 + chain.evidence.length * 90
    : 120 + Math.max(chain.evidence.length, 1) * 180;

  return (
    <section ref={ref} className={styles.wrapper} aria-label="Evidence chain">
      <div className={styles.canvas} style={{ height }}>
        <ReactFlow
          key={vertical ? 'v' : 'h'}
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          colorMode="dark"
          fitView
          fitViewOptions={{ padding: 0.1 }}
          nodesDraggable={false}
          nodesConnectable={false}
          zoomOnScroll={false}
          minZoom={0.2}
          proOptions={{ hideAttribution: true }}
        >
          <Background gap={24} />
        </ReactFlow>
      </div>
      <ul className={styles.srList} aria-label="Evidence results">
        {chain.evidence.map((item) => (
          <li key={item.id}>
            {KIND_LABEL[item.kind]} {item.ref}: {RESULT_LABEL[item.result ?? 'none']}
          </li>
        ))}
      </ul>
    </section>
  );
}
