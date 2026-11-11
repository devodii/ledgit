import { Outlet } from 'react-router-dom';
import { useMeta } from '@/api/hooks';
import { Footer } from '../Footer';
import { Header } from '../Header';
import styles from './AppShell.module.scss';

export function AppShell() {
  const meta = useMeta();
  return (
    <div className={styles.shell}>
      <a href="#main" className={styles.skip}>
        Skip to content
      </a>
      <Header />
      <main id="main" className={styles.main}>
        <Outlet />
      </main>
      <Footer lastVerifiedAt={meta.data?.last_verified_at} dataVersion={meta.data?.data_version} />
    </div>
  );
}
