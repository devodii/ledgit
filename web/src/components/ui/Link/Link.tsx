import { Link as RouterLink, type LinkProps } from 'react-router-dom';
import styles from './Link.module.scss';

export function Link({ className, ...rest }: LinkProps) {
  return <RouterLink className={[styles.link, className].filter(Boolean).join(' ')} {...rest} />;
}
