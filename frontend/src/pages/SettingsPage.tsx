import {
  Archive,
  Database,
  Download,
  HardDrive,
  Languages,
  Moon,
  RefreshCw,
  RotateCcw,
  Sun,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useOfflineSync } from "../app/OfflineSync";
import { usePreferences, type ThemePreference } from "../app/Preferences";
import { PageHeader, SectionHeader } from "../components/PageHeader";
import { useToast } from "../components/Toast";
import { Alert, Badge, Button, Card, Modal } from "../components/ui";
import { clearOfflineData, offlineDb } from "../services/offlineDb";
import { api } from "../services/api";

interface StorageDetails {
  usage: number;
  quota: number;
}

function bytes(value: number) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 ** 2).toFixed(1)} MB`;
}

export default function SettingsPage() {
  const { locale, setLocale, theme, setTheme, demoMode, setDemoMode } =
    usePreferences();
  const {
    online,
    pendingCount,
    failedCount,
    syncing,
    lastSyncedAt,
    syncNow,
    refreshCounts,
  } = useOfflineSync();
  const [storage, setStorage] = useState<StorageDetails>({
    usage: 0,
    quota: 0,
  });
  const [resetOpen, setResetOpen] = useState(false);
  const [demoResetOpen, setDemoResetOpen] = useState(false);
  const { notify } = useToast();
  const queryClient = useQueryClient();

  useEffect(() => {
    void navigator.storage
      ?.estimate()
      .then((estimate) =>
        setStorage({ usage: estimate.usage ?? 0, quota: estimate.quota ?? 0 }),
      );
  }, [pendingCount, failedCount]);

  const downloadBackup = async () => {
    const [drafts, queue, assessments] = await Promise.all([
      offlineDb.drafts.toArray(),
      offlineDb.queue.toArray(),
      offlineDb.assessments.toArray(),
    ]);
    const blob = new Blob(
      [
        JSON.stringify(
          {
            version: 1,
            exportedAt: new Date().toISOString(),
            drafts,
            queue,
            assessments,
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `mundasense-browser-backup-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    notify("Browser backup exported");
  };

  const resetBrowserData = async () => {
    await clearOfflineData();
    await refreshCounts();
    setResetOpen(false);
    notify("Offline drafts, queue, and cached results cleared");
  };

  const resetDemoData = async () => {
    const result = await api.resetDemoData();
    setDemoResetOpen(false);
    await queryClient.invalidateQueries();
    notify(
      `${result.removed_assessments} demonstration assessment${result.removed_assessments === 1 ? "" : "s"} removed`,
    );
  };

  const themes: Array<{
    id: ThemePreference;
    label: string;
    Icon: typeof Sun;
  }> = [
    { id: "light", label: "Light", Icon: Sun },
    { id: "dark", label: "Dark", Icon: Moon },
    { id: "system", label: "System", Icon: HardDrive },
  ];

  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Device preferences"
        title="Settings and offline storage"
        body="Preferences stay on this browser. Model inputs and stored database records remain metric and versioned."
      />
      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="p-5">
          <div className="flex items-center gap-3">
            <Languages className="size-6 text-teal" />
            <h2 className="text-xl font-extrabold text-ink">Language</h2>
          </div>
          <label className="mt-5 block">
            <span className="label">Interface language</span>
            <select
              className="input"
              value={locale}
              onChange={(event) => setLocale(event.target.value as "en" | "sn")}
            >
              <option value="en">English</option>
              <option value="sn">Shona · partial demonstration</option>
            </select>
            <span className="help block">
              Unreviewed Shona strings fall back to English.
            </span>
          </label>
        </Card>
        <Card className="p-5">
          <h2 className="text-xl font-extrabold text-ink">Theme</h2>
          <div className="mt-5 grid grid-cols-3 gap-2">
            {themes.map(({ id, label, Icon }) => (
              <button
                key={id}
                onClick={() => setTheme(id)}
                className={`grid min-h-24 place-items-center rounded-xl border p-3 text-sm font-bold ${theme === id ? "border-teal bg-teal/10 text-teal" : "border-line bg-pale text-muted"}`}
                aria-pressed={theme === id}
              >
                <Icon className="size-5" />
                {label}
              </button>
            ))}
          </div>
        </Card>
      </div>
      <SectionHeader title="Demonstration and defaults" />
      <Card className="p-5">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-extrabold text-ink">Demonstration mode</h2>
            <p className="mt-1 text-sm text-muted">
              Show judge-ready scenario shortcuts and explicit synthetic-data
              labels.
            </p>
          </div>
          <button
            role="switch"
            aria-checked={demoMode}
            onClick={() => setDemoMode(!demoMode)}
            className={`relative h-8 w-14 rounded-full transition ${demoMode ? "bg-teal" : "bg-slate-400"}`}
          >
            <span
              className={`absolute top-1 size-6 rounded-full bg-white shadow transition ${demoMode ? "left-7" : "left-1"}`}
            />
          </button>
        </div>
        <div className="mt-5 border-t border-line pt-5">
          <p className="text-sm font-bold text-ink">Default units</p>
          <p className="mt-1 text-sm text-muted">
            Metric · rainfall in millimetres, temperature in °C, inputs in
            kg/ha, area in hectares, yield in t/ha.
          </p>
        </div>
      </Card>
      <SectionHeader title="Synchronization" />
      <Card className="p-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone={online ? "green" : "gold"}>
            {online ? "Browser online" : "Browser offline"}
          </Badge>
          <Badge tone={pendingCount ? "gold" : "green"}>
            {pendingCount} pending
          </Badge>
          <Badge tone={failedCount ? "red" : "neutral"}>
            {failedCount} retrying
          </Badge>
        </div>
        <p className="mt-4 text-sm text-muted">
          {lastSyncedAt
            ? `Last successful sync ${new Date(lastSyncedAt).toLocaleString()}.`
            : "No browser queue synchronization has completed yet."}
        </p>
        <Button
          className="mt-4"
          onClick={() => void syncNow()}
          disabled={!online || syncing}
        >
          <RefreshCw className={`size-4 ${syncing ? "animate-spin" : ""}`} />
          {syncing ? "Synchronizing" : "Sync now"}
        </Button>
      </Card>
      <SectionHeader title="Storage, export, and reset" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <Database className="size-6 text-teal" />
          <h2 className="mt-4 font-extrabold text-ink">Browser storage</h2>
          <p className="mt-2 text-sm text-muted">
            {bytes(storage.usage)} used
            {storage.quota ? ` of ${bytes(storage.quota)} available` : ""}.
          </p>
        </Card>
        <Card className="p-5">
          <Archive className="size-6 text-teal" />
          <h2 className="mt-4 font-extrabold text-ink">
            Export browser backup
          </h2>
          <p className="mt-2 text-sm text-muted">
            Download local drafts, queued records, and cached results as JSON.
          </p>
          <Button
            className="mt-4"
            variant="secondary"
            onClick={() => void downloadBackup()}
          >
            <Download className="size-4" />
            Export backup
          </Button>
        </Card>
        <Card className="p-5">
          <RotateCcw className="size-6 text-risk" />
          <h2 className="mt-4 font-extrabold text-ink">Reset offline data</h2>
          <p className="mt-2 text-sm text-muted">
            Clears browser-only data. Server history is not deleted.
          </p>
          <Button
            className="mt-4"
            variant="danger"
            onClick={() => setResetOpen(true)}
          >
            Reset browser data
          </Button>
        </Card>
        <Card className="p-5">
          <RotateCcw className="size-6 text-gold" />
          <h2 className="mt-4 font-extrabold text-ink">
            Reset demo assessments
          </h2>
          <p className="mt-2 text-sm text-muted">
            Removes synthetic demo and scenario assessments from SQLite. Manual
            records remain.
          </p>
          <Button
            className="mt-4"
            variant="secondary"
            onClick={() => setDemoResetOpen(true)}
          >
            Reset demo data
          </Button>
        </Card>
      </div>
      <div className="mt-5">
        <Alert tone="info" title="Application version">
          MundaSense AI 0.2.0 · local-first hackathon demonstration build.
        </Alert>
      </div>
      <Modal
        open={resetOpen}
        title="Clear browser-only data?"
        onClose={() => setResetOpen(false)}
      >
        <p className="leading-7 text-muted">
          This removes drafts, unsynchronized queue items, and cached results
          from this browser profile. It cannot be undone. Assessments already
          synchronized to SQLite remain available.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setResetOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => void resetBrowserData()}>
            Clear offline data
          </Button>
        </div>
      </Modal>
      <Modal
        open={demoResetOpen}
        title="Remove demonstration assessments?"
        onClose={() => setDemoResetOpen(false)}
      >
        <p className="leading-7 text-muted">
          This permanently removes records labelled as demo or scenario data
          from the local SQLite database. Manual assessments remain. Run the
          seed command to recreate the judge-ready data set.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setDemoResetOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => void resetDemoData()}>
            Remove demo assessments
          </Button>
        </div>
      </Modal>
    </div>
  );
}
