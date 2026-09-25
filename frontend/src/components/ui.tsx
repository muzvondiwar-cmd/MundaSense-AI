import { AlertTriangle, CheckCircle2, Info, LoaderCircle, X } from "lucide-react";
import { useEffect, useRef, type ButtonHTMLAttributes, type HTMLAttributes, type ReactNode } from "react";

export function Button({ className = "", variant = "primary", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger" }) {
  return <button className={`button button-${variant} ${className}`} {...props} />;
}

export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={`card ${className}`} {...props} />;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "green" | "gold" | "red" | "teal" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export function Alert({ children, tone = "info", title }: { children: ReactNode; tone?: "info" | "warning" | "critical" | "success"; title?: string }) {
  const Icon = tone === "critical" || tone === "warning" ? AlertTriangle : tone === "success" ? CheckCircle2 : Info;
  return (
    <div className={`alert alert-${tone}`} role={tone === "critical" ? "alert" : "status"}>
      <Icon className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
      <div>{title && <strong className="mb-1 block text-ink">{title}</strong>}{children}</div>
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />;
}

export function PageSkeleton() {
  return <div className="space-y-4" aria-label="Loading local data"><Skeleton className="h-10 w-2/3" /><Skeleton className="h-24 w-full" /><div className="grid gap-4 md:grid-cols-3"><Skeleton className="h-40" /><Skeleton className="h-40" /><Skeleton className="h-40" /></div></div>;
}

export function EmptyState({ icon, title, body, action }: { icon: ReactNode; title: string; body: string; action?: ReactNode }) {
  return <Card className="grid min-h-64 place-items-center p-8 text-center"><div><div className="mx-auto mb-4 grid size-12 place-items-center rounded-2xl bg-pale text-green-800">{icon}</div><h2 className="text-xl font-extrabold text-ink">{title}</h2><p className="mx-auto mt-2 max-w-md text-muted">{body}</p>{action && <div className="mt-5">{action}</div>}</div></Card>;
}

export function Spinner({ label = "Loading" }: { label?: string }) {
  return <span className="inline-flex items-center gap-2"><LoaderCircle className="size-4 animate-spin motion-reduce:animate-none" aria-hidden="true" />{label}</span>;
}

export function Modal({ open, title, children, onClose }: { open: boolean; title: string; children: ReactNode; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);
  return <dialog ref={ref} onCancel={onClose} onClose={onClose} className="modal"><div className="flex items-center justify-between gap-4"><h2 className="text-xl font-extrabold text-ink">{title}</h2><button onClick={onClose} className="icon-button" aria-label="Close dialog"><X className="size-5" /></button></div><div className="mt-4">{children}</div></dialog>;
}
