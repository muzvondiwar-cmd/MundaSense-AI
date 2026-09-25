import { useQuery } from "@tanstack/react-query";
import { Beaker, FileText, History, Plus } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { usePreferences } from "../app/Preferences";
import { ResultView } from "../components/ResultView";
import { Alert, PageSkeleton } from "../components/ui";
import { api } from "../services/api";

export default function ResultPage() {
  const { id = "" } = useParams();
  const { locale } = usePreferences();
  const result = useQuery({ queryKey: ["assessment", id, locale], queryFn: () => api.getAssessment(id, locale), enabled: Boolean(id) });
  if (result.isLoading) return <PageSkeleton />;
  if (!result.data) return <Alert tone="critical" title="Result unavailable">This assessment could not be loaded from local history. Check the ID or retry when the backend is ready.</Alert>;
  const actions = <><a href={api.reportUrl(id)} target="_blank" rel="noreferrer" className="button button-secondary"><FileText className="size-4" />Print passport</a><Link to={`/scenario-lab?baseline=${encodeURIComponent(id)}`} className="button button-secondary"><Beaker className="size-4" />Scenario baseline</Link><Link to="/history" className="button button-ghost"><History className="size-4" />History</Link><Link to="/assess/new" className="button button-primary"><Plus className="size-4" />New assessment</Link></>;
  return <ResultView result={result.data} actions={actions} />;
}
