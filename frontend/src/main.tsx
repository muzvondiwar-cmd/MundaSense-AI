import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";
import { OfflineSyncProvider } from "./app/OfflineSync";
import { PreferencesProvider } from "./app/Preferences";
import { ToastProvider } from "./components/Toast";
import "./styles/index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1, refetchOnWindowFocus: false },
    mutations: { retry: false },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <PreferencesProvider>
        <ToastProvider>
          <OfflineSyncProvider>
            <App />
          </OfflineSyncProvider>
        </ToastProvider>
      </PreferencesProvider>
    </QueryClientProvider>
  </StrictMode>,
);
