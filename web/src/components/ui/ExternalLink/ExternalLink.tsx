import type { AnchorHTMLAttributes, ReactNode } from 'react';
import { Icon } from '../Icon';
import styles from './ExternalLink.module.scss';

export interface ExternalLinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  children: ReactNode;
}

export function ExternalLink({ href, children, className, ...rest }: ExternalLinkProps) {
  return (
    <a
      href={href}
      className={[styles.link, className].filter(Boolean).join(' ')}
      target="_blank"
      rel="noopener noreferrer"
      {...rest}
    >
      {children}
      <Icon name="external" size="sm" />
      <span className={styles.hint}> (opens in a new tab)</span>
    </a>
  );
}
