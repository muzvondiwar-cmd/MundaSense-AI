import { Eye, Languages, Leaf, LockKeyhole, ShieldAlert, UserRoundCheck } from "lucide-react";
import { Link } from "react-router-dom";

import { PageHeader, SectionHeader } from "../components/PageHeader";
import { Alert, Badge, Card } from "../components/ui";

export default function AboutPage() {
  return <div className="page-enter">
    <PageHeader eyebrow="Purpose, limits, and privacy" title="Responsible maize decision support" body="MundaSense helps farmers and extension officers organize five seasonal observations, understand a local model estimate, and start a safer conversation." />
    <div className="grid gap-4 md:grid-cols-2"><Card className="bg-gradient-to-br from-deep to-leaf p-6 text-white"><Leaf className="size-7" /><h2 className="mt-4 text-2xl font-extrabold text-white">Intended purpose</h2><p className="mt-3 leading-7 text-green-50">Estimate a plausible maize-yield range, surface provisional risk and confidence, explain model associations, flag unfamiliar inputs, and offer one cautious rule-based next step.</p></Card><Card className="p-6"><ShieldAlert className="size-7 text-gold" /><h2 className="mt-4 text-2xl font-extrabold text-ink">Not intended for</h2><p className="mt-3 leading-7 text-muted">Autonomous agronomy, exact dose or chemical prescriptions, irrigation automation, insurance, credit, legal decisions, guaranteed outcomes, or replacement of field inspection.</p></Card></div>
    <SectionHeader title="Safety by design" />
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{[
      [LockKeyhole, "Local by default", "Inputs, results, model inference, rules, and SQLite history remain on this device."],
      [Eye, "Uncertainty stays visible", "Plausible range, confidence, unusual-input warnings, and limitations remain close to the result."],
      [UserRoundCheck, "Human referral", "High risk, weak confidence, or severe data warnings can require extension review."],
      [Languages, "English fallback", "Reviewed Shona core strings are reused. Unreviewed wording safely falls back to English."],
    ].map(([Icon, title, body]) => <Card key={title as string} className="p-5"><Icon className="size-6 text-teal" /><h3 className="mt-4 font-extrabold text-ink">{title as string}</h3><p className="mt-2 text-sm leading-6 text-muted">{body as string}</p></Card>)}</div>
    <SectionHeader title="Data handling" />
    <Card className="p-5"><div className="flex flex-wrap gap-2"><Badge tone="green">No cloud account</Badge><Badge tone="green">No trackers</Badge><Badge tone="teal">Coarse location only</Badge><Badge tone="gold">Device owner controls retention</Badge></div><p className="mt-4 max-w-4xl leading-7 text-slate-700">The app does not ask for a legal name, national ID, phone number, exact GPS position, or financial information. A field reference should be a non-sensitive alias. The device owner is responsible for access control, backups, retention choices, and secure deletion.</p></Card>
    <div className="mt-5"><Alert tone="warning" title="Human review still required">The Shona catalogue and every agronomic advisory rule require bilingual and qualified local agronomic review before field deployment. English remains authoritative for this demonstration.</Alert></div>
    <div className="mt-7 flex flex-wrap gap-3"><Link to="/model" className="button button-secondary">Read the model card</Link><Link to="/assess/new" className="button button-primary">Start a maize assessment</Link></div>
  </div>;
}
