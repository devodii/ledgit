import * as RadixTabs from '@radix-ui/react-tabs';
import type { ReactNode } from 'react';
import styles from './Tabs.module.scss';

export interface TabsProps {
  tabs: Array<{ value: string; label: string; content: ReactNode }>;
  defaultValue?: string;
}

export function Tabs({ tabs, defaultValue }: TabsProps) {
  return (
    <RadixTabs.Root defaultValue={defaultValue ?? tabs[0]?.value} className={styles.root}>
      <RadixTabs.List className={styles.list}>
        {tabs.map((tab) => (
          <RadixTabs.Trigger key={tab.value} value={tab.value} className={styles.trigger}>
            {tab.label}
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      {tabs.map((tab) => (
        <RadixTabs.Content key={tab.value} value={tab.value} className={styles.content}>
          {tab.content}
        </RadixTabs.Content>
      ))}
    </RadixTabs.Root>
  );
}
