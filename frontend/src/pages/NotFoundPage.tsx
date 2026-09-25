import { Compass } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/ui";

export default function NotFoundPage() {
  return <EmptyState icon={<Compass className="size-6" />} title="This route is not part of the field map" body="The page may have moved, or the assessment link is incomplete. Your local records have not been changed." action={<Link className="button button-primary" to="/">Return home</Link>} />;
}
