import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Skeleton } from './components/ui/Skeleton';
import { ToastProvider } from './components/ui/Toast';
const AdminTasksPage = lazy(() =>
  import('./pages/AdminTasksPage').then((m) => ({ default: m.AdminTasksPage })),
);
const ChangesPage = lazy(() =>
  import('./pages/ChangesPage').then((m) => ({ default: m.ChangesPage })),
);
const ClaimPage = lazy(() => import('./pages/ClaimPage').then((m) => ({ default: m.ClaimPage })));
import { ErrorBoundary } from './pages/ErrorPage';
import { HomePage } from './pages/HomePage';
const MethodologyPage = lazy(() =>
  import('./pages/MethodologyPage').then((m) => ({ default: m.MethodologyPage })),
);
import { NotFoundPage } from './pages/NotFoundPage';
const OpenAsksPage = lazy(() =>
  import('./pages/OpenAsksPage').then((m) => ({ default: m.OpenAsksPage })),
);
const OrgPage = lazy(() => import('./pages/OrgPage').then((m) => ({ default: m.OrgPage })));

export function App() {
  return (
    <ToastProvider>
      <ErrorBoundary>
        <Suspense fallback={<Skeleton height="30rem" />}>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/claims/:id" element={<ClaimPage />} />
              <Route path="/orgs/:slug" element={<OrgPage />} />
              <Route path="/open-asks" element={<OpenAsksPage />} />
              <Route path="/changes" element={<ChangesPage />} />
              <Route path="/methodology" element={<MethodologyPage />} />
              <Route path="/admin/tasks" element={<AdminTasksPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </ToastProvider>
  );
}
