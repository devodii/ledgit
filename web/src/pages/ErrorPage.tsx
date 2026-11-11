import { Component, type ReactNode } from 'react';
import { ErrorState } from '@/components/ui/ErrorState';

export class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error) {
    window.dispatchEvent(new CustomEvent('ledgit:error', { detail: error }));
  }

  render() {
    if (this.state.error) {
      return <ErrorState onRetry={() => this.setState({ error: null })} />;
    }
    return this.props.children;
  }
}
