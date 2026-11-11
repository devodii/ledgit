import { useQuery } from '@tanstack/react-query';

async function fetchHealth(): Promise<{ status: string }> {
  const response = await fetch('/api/v1/health');
  if (!response.ok) throw new Error(`health returned ${response.status}`);
  return response.json();
}

export function HomePage() {
  const { data, isError, isPending } = useQuery({ queryKey: ['health'], queryFn: fetchHealth });

  return (
    <main>
      <h1>Ledgit</h1>
      <p>What the Stellar network says about claims made on stage.</p>
      <p role="status">
        {isPending && 'Checking API'}
        {isError && 'API unreachable'}
        {data && `API ${data.status}`}
      </p>
    </main>
  );
}
