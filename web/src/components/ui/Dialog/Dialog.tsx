import * as RadixDialog from '@radix-ui/react-dialog';
import type { ReactNode } from 'react';
import { IconButton } from '../IconButton';
import styles from './Dialog.module.scss';

export interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  variant?: 'dialog' | 'drawer';
  children: ReactNode;
}

export function Dialog({
  open,
  onOpenChange,
  title,
  description,
  variant = 'dialog',
  children,
}: DialogProps) {
  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className={styles.overlay} />
        <RadixDialog.Content className={`${styles.content} ${styles[variant]}`}>
          <header className={styles.header}>
            <RadixDialog.Title className={styles.title}>{title}</RadixDialog.Title>
            <RadixDialog.Close asChild>
              <IconButton icon="x" label="Close" size="sm" />
            </RadixDialog.Close>
          </header>
          {description ? (
            <RadixDialog.Description className={styles.description}>
              {description}
            </RadixDialog.Description>
          ) : (
            <RadixDialog.Description className={styles.description}>
              {title}
            </RadixDialog.Description>
          )}
          {children}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  );
}
