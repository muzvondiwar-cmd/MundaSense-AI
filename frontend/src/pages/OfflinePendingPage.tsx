import { CloudOff, History, RefreshCw } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { useOfflineSync } from "../app/OfflineSync";
import { PageHeader } from "../components/PageHeader";
import { Alert, Badge, Button, Card } from "../components/ui";

export default function OfflinePendingPage() {
  const { id = "" } = useParams();
  const { online, pendingCount, failedCount, syncing, syncNow } =
    useOfflineSync();
  return (
    <div className="page-enter">
      <PageHeader
        eyebrow="Offline assessment"
        title="Saved offline—prediction pending"
        body="Your measurements are safely queued on this device. MundaSense will not invent a result while the Python prediction service is unavailable."
      />
      <Card className="mx-auto max-w-3xl p-6 sm:p-8">
        <div className="grid size-14 place-items-center rounded-2xl bg-amber-100 text-gold">
          <CloudOff className="size-7" />
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          <Badge tone={online ? "teal" : "gold"}>
            {online ? "Network detected" : "Offline"}
          </Badge>
          <Badge tone="neutral">Queue ID {id.slice(0, 8)}</Badge>
          <Badge tone={failedCount ? "red" : "gold"}>
            {pendingCount + failedCount} waiting
          </Badge>
        </div>
        <h2 className="mt-5 text-2xl font-extrabold text-ink">
          What happens next
        </h2>
        <ol className="mt-4 grid gap-3 text-sm leading-6 text-muted">
          <li>
            <strong className="text-ink">1.</strong> Keep this browser profile
            and local storage intact.
          </li>
          <li>
            <strong className="text-ink">2.</strong> Reconnect to the laptop or
            local server running MundaSense.
          </li>
          <li>
            <strong className="text-ink">3.</strong> The same idempotency key is
            retried, preventing duplicate assessments.
          </li>
          <li>
            <strong className="text-ink">4.</strong> Open History after
            synchronization to view the genuine model result.
          </li>
        </ol>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button onClick={() => void syncNow()} disabled={!online || syncing}>
            <RefreshCw className={`size-4 ${syncing ? "animate-spin" : ""}`} />
            {syncing ? "Synchronizing" : "Sync now"}
          </Button>
          <Link to="/history" className="button button-secondary">
            <History className="size-4" />
            Open history
          </Link>
        </div>
      </Card>
      <div className="mx-auto mt-5 max-w-3xl">
        <Alert tone="warning" title="No offline prediction is shown">
          A final result requires the versioned local model, validation rules,
          explanations, and advisory engine. The queued record contains inputs
          only.
        </Alert>
      </div>
    </div>
  );
}
