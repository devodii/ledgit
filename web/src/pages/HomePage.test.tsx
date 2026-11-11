import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { HomePage } from './HomePage';

afterEach(() => vi.unstubAllGlobals());

it('shows the API status once the health call resolves', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok' }) }),
  );
  render(
    <QueryClientProvider client={new QueryClient()}>
      <HomePage />
    </QueryClientProvider>,
  );
  expect(await screen.findByText('API ok')).toBeInTheDocument();
});
