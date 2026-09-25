import { useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { useToast } from "../components/Toast";
import { api } from "../services/api";
import {
  dueQueueRecords,
  markQueueFailed,
  offlineEvents,
  queueCounts,
  removeQueued,
} from "../services/offlineDb";

interface OfflineSyncValue {
  online: boolean;
  pendingCount: number;
  failedCount: number;
  syncing: boolean;
  lastSyncedAt: string | null;
  syncNow: () => Promise<void>;
  refreshCounts: () => Promise<void>;
}

const OfflineSyncContext = createContext<OfflineSyncValue | null>(null);

export function OfflineSyncProvider({ children }: { children: ReactNode }) {
  const [online, setOnline] = useState(() => navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);
  const [failedCount, setFailedCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(() =>
    localStorage.getItem("mundasense.v1.last-sync"),
  );
  const queryClient = useQueryClient();
  const { notify } = useToast();

  const refreshCounts = useCallback(async () => {
    const counts = await queueCounts();
    setPendingCount(counts.pending);
    setFailedCount(counts.failed);
  }, []);

  const syncNow = useCallback(async () => {
    if (!navigator.onLine || syncing) return;
    const records = await dueQueueRecords();
    if (!records.length) {
      await refreshCounts();
      return;
    }
    setSyncing(true);
    try {
      const response = await api.syncBatch({
        items: records.map((item) => ({
          entity_type: item.entityType,
          idempotency_key: item.idempotencyKey,
          payload: item.payload,
        })),
      });
      await Promise.all(
        response.items.map(async (item) => {
          if (item.status === "synchronized")
            await removeQueued(item.idempotency_key);
          else
            await markQueueFailed(
              item.idempotency_key,
              item.error ?? "Synchronization failed",
            );
        }),
      );
      const timestamp = new Date().toISOString();
      localStorage.setItem("mundasense.v1.last-sync", timestamp);
      setLastSyncedAt(timestamp);
      await queryClient.invalidateQueries();
      if (response.synchronized)
        notify(
          `${response.synchronized} offline record${response.synchronized === 1 ? "" : "s"} synchronized`,
        );
    } catch (error) {
      await Promise.all(
        records.map((item) =>
          markQueueFailed(
            item.idempotencyKey,
            error instanceof Error ? error.message : "Backend unavailable",
          ),
        ),
      );
    } finally {
      setSyncing(false);
      await refreshCounts();
    }
  }, [notify, queryClient, refreshCounts, syncing]);

  useEffect(() => {
    const handleOnline = () => {
      setOnline(true);
      void syncNow();
    };
    const handleOffline = () => setOnline(false);
    const handleChange = () => void refreshCounts();
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    offlineEvents.addEventListener("change", handleChange);
    void refreshCounts();
    const timer = window.setInterval(() => {
      if (navigator.onLine) void syncNow();
    }, 30_000);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      offlineEvents.removeEventListener("change", handleChange);
      window.clearInterval(timer);
    };
  }, [refreshCounts, syncNow]);

  const value = useMemo(
    () => ({
      online,
      pendingCount,
      failedCount,
      syncing,
      lastSyncedAt,
      syncNow,
      refreshCounts,
    }),
    [
      online,
      pendingCount,
      failedCount,
      syncing,
      lastSyncedAt,
      syncNow,
      refreshCounts,
    ],
  );
  return (
    <OfflineSyncContext.Provider value={value}>
      {children}
    </OfflineSyncContext.Provider>
  );
}

export function useOfflineSync() {
  const value = useContext(OfflineSyncContext);
  if (!value)
    throw new Error("useOfflineSync must be used inside OfflineSyncProvider");
  return value;
}
