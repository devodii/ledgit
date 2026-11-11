/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_EVENT_SLUG?: string;
  readonly VITE_GITHUB_REPO?: string;
  readonly VITE_SITE_URL?: string;
  readonly VITE_ERROR_ENDPOINT?: string;
}
