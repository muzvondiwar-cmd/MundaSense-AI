import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Beaker, FileText, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { usePreferences } from "../app/Preferences";
import { ResultView } from "../components/ResultView";
import { useToast } from "../components/Toast";
import { Alert, Button, Modal, PageSkeleton } from "../components/ui";
import { api } from "../services/api";

export default function CaseDetailPage() {
  const { id = "" } = useParams();
  const [confirming, setConfirming] = useState(false);
  const { locale } = usePreferences();
  const { notify } = useToast();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const result = useQuery({
    queryKey: ["assessment", id, locale],
    queryFn: () => api.getAssessment(id, locale),
    enabled: Boolean(id),
  });
  const remove = useMutation({
    mutationFn: () => api.deleteAssessment(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["history"] });
      notify("Assessment permanently deleted");
      navigate("/history");
    },
  });
  if (result.isLoading) return <PageSkeleton />;
  if (!result.data)
    return (
      <Alert tone="critical" title="Saved case unavailable">
        The immutable snapshot was not found in the local database.
      </Alert>
    );
  const actions = (
    <>
      <a
        href={api.reportUrl(id)}
        target="_blank"
        rel="noreferrer"
        className="button button-secondary"
      >
        <FileText className="size-4" />
        Print passport
      </a>
      <Link
        to={`/scenario-lab?baseline=${encodeURIComponent(id)}`}
        className="button button-secondary"
      >
        <Beaker className="size-4" />
        Scenario baseline
      </Link>
      <Link to="/assess/new" className="button button-primary">
        <Plus className="size-4" />
        New assessment
      </Link>
      <Button variant="ghost" onClick={() => setConfirming(true)}>
        <Trash2 className="size-4" />
        Delete
      </Button>
    </>
  );
  return (
    <>
      <ResultView
        result={result.data}
        title="Immutable case detail"
        actions={actions}
      />
      <Modal
        open={confirming}
        onClose={() => setConfirming(false)}
        title="Delete this local assessment?"
      >
        <Alert tone="critical" title="Permanent deletion">
          This will permanently remove assessment{" "}
          <span className="break-all font-mono">{id}</span> from this device. It
          cannot be undone.
        </Alert>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirming(false)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            disabled={remove.isPending}
            onClick={() => remove.mutate()}
          >
            {remove.isPending ? "Deleting…" : "Delete exact assessment"}
          </Button>
        </div>
      </Modal>
    </>
  );
}
