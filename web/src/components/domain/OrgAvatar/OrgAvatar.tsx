import styles from './OrgAvatar.module.scss';

export interface OrgAvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg';
}

export function OrgAvatar({ name, size = 'md' }: OrgAvatarProps) {
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase())
    .join('');
  return (
    <span className={`${styles.avatar} ${styles[size]}`} aria-hidden="true">
      {initials}
    </span>
  );
}
