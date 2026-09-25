import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  body,
  actions,
}: {
  eyebrow: string;
  title: string;
  body: string;
  actions?: ReactNode;
}) {
  return (
    <header className="page-enter mb-7 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl">
        <p className="text-xs font-extrabold uppercase tracking-[.15em] text-teal">
          {eyebrow}
        </p>
        <h1 className="mt-2 text-4xl font-black leading-tight text-ink sm:text-5xl">
          {title}
        </h1>
        <p className="mt-3 text-base leading-7 text-muted sm:text-lg">{body}</p>
      </div>
      {actions && (
        <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>
      )}
    </header>
  );
}

export function SectionHeader({
  title,
  body,
}: {
  title: string;
  body?: string;
}) {
  return (
    <div className="mb-4 mt-9 flex flex-col gap-1 md:flex-row md:items-end md:justify-between">
      <h2 className="text-2xl font-extrabold text-ink sm:text-3xl">{title}</h2>
      {body && <p className="max-w-xl text-sm leading-6 text-muted">{body}</p>}
    </div>
  );
}
