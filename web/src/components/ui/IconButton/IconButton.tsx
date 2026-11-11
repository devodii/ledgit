import type { ButtonHTMLAttributes } from 'react';
import { Icon, type IconName } from '../Icon';
import styles from './IconButton.module.scss';

export interface IconButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  icon: IconName;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'secondary' | 'ghost';
}

export function IconButton({
  icon,
  label,
  size = 'md',
  variant = 'ghost',
  className,
  type = 'button',
  ...rest
}: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={[styles.button, styles[size], styles[variant], className]
        .filter(Boolean)
        .join(' ')}
      {...rest}
    >
      <Icon name={icon} size={size === 'lg' ? 'lg' : size === 'sm' ? 'sm' : 'md'} />
    </button>
  );
}
