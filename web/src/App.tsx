import { Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { ToastProvider } from './components/ui/Toast';
import { AdminTasksPage } from './pages/AdminTasksPage';
import { ChangesPage } from './pages/ChangesPage';
import { ClaimPage } from './pages/ClaimPage';
import { ErrorBoundary } from './pages/ErrorPage';
import { HomePage } from './pages/HomePage';
import { MethodologyPage } from './pages/MethodologyPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { OpenAsksPage } from './pages/OpenAsksPage';
import { OrgPage } from './pages/OrgPage';

export function App() {
  return (
    <ToastProvider>
      <ErrorBoundary>
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
      </ErrorBoundary>
    </ToastProvider>
  );
}
