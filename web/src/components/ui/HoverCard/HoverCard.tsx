import * as Tooltip from '@radix-ui/react-tooltip';
import type { ReactElement, ReactNode } from 'react';
import styles from './HoverCard.module.scss';

export interface HoverCardProps {
  children: ReactElement;
  content: ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export function HoverCard({ children, content, side = 'top' }: HoverCardProps) {
  return (
    <Tooltip.Provider delayDuration={80} skipDelayDuration={300}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            className={styles.content}
            side={side}
            sideOffset={10}
            collisionPadding={12}
          >
            {content}
            <Tooltip.Arrow className={styles.arrow} />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
