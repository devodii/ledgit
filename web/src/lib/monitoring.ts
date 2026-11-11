interface ReportedError {
  message: string;
  stack?: string;
  url: string;
  when: string;
}

const ENDPOINT = import.meta.env.VITE_ERROR_ENDPOINT as string | undefined;

function send(error: ReportedError) {
  if (!ENDPOINT) {
    console.error('[ledgit]', error.message);
    return;
  }
  const body = JSON.stringify(error);
  if (!navigator.sendBeacon?.(ENDPOINT, body)) {
    void fetch(ENDPOINT, { method: 'POST', body, keepalive: true }).catch(() => undefined);
  }
}

export function installMonitoring() {
  const report = (reason: unknown) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    send({
      message: error.message,
      stack: error.stack,
      url: location.href,
      when: new Date().toISOString(),
    });
  };
  window.addEventListener('error', (event) => report(event.error ?? event.message));
  window.addEventListener('unhandledrejection', (event) => report(event.reason));
  window.addEventListener('ledgit:error', (event) => report((event as CustomEvent).detail));
}
