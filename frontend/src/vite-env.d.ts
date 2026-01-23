/// <reference types="vite/client" />

/**
 * Vite environment variables type definitions.
 * Add your custom env variables here for TypeScript autocomplete.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
