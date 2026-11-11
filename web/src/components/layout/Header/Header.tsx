import { NavLink } from 'react-router-dom';
import styles from './Header.module.scss';

const LINKS = [
  { to: '/', label: 'Claims', end: true },
  { to: '/open-asks', label: 'Open asks' },
  { to: '/changes', label: 'Changes' },
  { to: '/methodology', label: 'Methodology' },
];

export function Header() {
  return (
    <header className={styles.header}>
      <NavLink to="/" className={styles.brand} aria-label="Ledgit home">
        Ledgit
      </NavLink>
      <nav aria-label="Main">
        <ul className={styles.nav}>
          {LINKS.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                end={link.end}
                className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
              >
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
