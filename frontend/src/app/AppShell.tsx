import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  BarChart3,
  Beaker,
  BookOpen,
  Building2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Cloud,
  History,
  Home,
  Info,
  Languages,
  Lightbulb,
  Menu,
  Plus,
  RefreshCw,
  Settings,
  ShieldCheck,
  WifiOff,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { Badge } from "../components/ui";
import { translate } from "../i18n/translations";
import { api } from "../services/api";
import { usePreferences } from "./Preferences";
import { ServiceWorkerUpdate } from "./ServiceWorkerUpdate";
import { useOfflineSync } from "./OfflineSync";

const farmerNav = [
  ["/", "nav.home", Home],
  ["/assess/new", "nav.assess", ClipboardList],
  ["/farms", "nav.farms", Building2],
  ["/scenario-lab", "nav.scenario", Beaker],
  ["/history", "nav.history", History],
  ["/dashboard", "nav.dashboard", BarChart3],
  ["/insights", "nav.insights", Lightbulb],
  ["/model", "nav.model", BookOpen],
  ["/about", "nav.about", Info],
  ["/settings", "nav.settings", Settings],
] as const;

const titles: Record<string, string> = {
  "/": "Home",
  "/assess/new": "New assessment",
  "/scenario-lab": "Climate Scenario Lab",
  "/dashboard": "Extension dashboard",
  "/history": "Assessment history",
  "/model": "Model card",
  "/about": "About & safety",
  "/farms": "Farms & fields",
  "/insights": "Insights",
  "/settings": "Settings",
  "/offline/pending": "Offline assessment",
};

function Navigation({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  const { locale, mode } = usePreferences();
  const nav = useMemo(
    () =>
      mode === "officer"
        ? [
            farmerNav[0],
            farmerNav[4],
            farmerNav[3],
            farmerNav[1],
            farmerNav[2],
            farmerNav[5],
            farmerNav[6],
          ]
        : farmerNav,
    [mode],
  );
  return (
    <nav aria-label="Primary navigation" className="grid gap-1">
      {nav.map(([href, key, Icon]) => (
        <NavLink
          key={href}
          to={href}
          onClick={onNavigate}
          end={href === "/"}
          className={({ isActive }) =>
            `flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold transition ${isActive ? "bg-green-100 text-deep" : "text-slate-600 hover:bg-green-50 hover:text-ink"}`
          }
          title={collapsed ? translate(locale, key) : undefined}
        >
          <Icon className="size-5 shrink-0" aria-hidden="true" />
          {!collapsed && <span>{translate(locale, key)}</span>}
        </NavLink>
      ))}
    </nav>
  );
}

function MobileNavigation({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
      className="fixed inset-0 m-0 h-full max-h-none w-full max-w-none bg-transparent p-0 backdrop:bg-ink/45 lg:hidden"
      aria-label="Mobile navigation"
    >
      <aside className="h-full w-[min(86vw,20rem)] bg-white p-4 shadow-2xl">
        <div className="mb-6 flex items-center justify-between">
          <img
            src="/mundasense_logo.png"
            alt="MundaSense AI"
            className="w-44"
          />
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <X className="size-5" />
          </button>
        </div>
        <Navigation onNavigate={onClose} />
      </aside>
    </dialog>
  );
}

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { locale, setLocale, mode, setMode } = usePreferences();
  const { online, pendingCount, failedCount, syncing, syncNow } =
    useOfflineSync();
  const location = useLocation();
  const health = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30_000,
    retry: 1,
    enabled: online,
  });
  const pageTitle =
    Object.entries(titles).find(
      ([path]) => path !== "/" && location.pathname.startsWith(path),
    )?.[1] ??
    titles[location.pathname] ??
    "MundaSense AI";
  useEffect(() => setMobileOpen(false), [location.pathname]);

  return (
    <div className="app-background min-h-screen">
      <a
        href="#main-content"
        className="fixed left-3 top-3 z-[100] -translate-y-24 rounded-lg bg-white px-4 py-2 font-bold text-ink shadow focus:translate-y-0"
      >
        Skip to content
      </a>
      <aside
        className={`fixed inset-y-0 left-0 z-40 hidden border-r border-line bg-white/90 p-4 backdrop-blur-xl transition-[width] lg:block ${collapsed ? "w-20" : "w-64"}`}
      >
        <div className="mb-6 flex min-h-14 items-center justify-between gap-2">
          {!collapsed && (
            <img
              src="/mundasense_logo.png"
              alt="MundaSense AI"
              className="h-auto w-44"
            />
          )}
          <button
            className="icon-button"
            onClick={() => setCollapsed((value) => !value)}
            aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
          >
            {collapsed ? (
              <ChevronRight className="size-5" />
            ) : (
              <ChevronLeft className="size-5" />
            )}
          </button>
        </div>
        <Navigation collapsed={collapsed} />
        <div className="absolute bottom-4 left-4 right-4 border-t border-line pt-4">
          {collapsed ? (
            <span
              className={`mx-auto block size-3 rounded-full ${health.data?.ready ? "bg-green-600" : online ? "bg-gold" : "bg-risk"}`}
              aria-label={
                health.data?.ready
                  ? "Local system ready"
                  : online
                    ? "Backend unavailable"
                    : "Browser offline"
              }
            />
          ) : (
            <div className="space-y-2">
              <Badge
                tone={health.data?.ready ? "green" : online ? "gold" : "red"}
              >
                {health.data?.ready ? (
                  <ShieldCheck className="size-3.5" />
                ) : (
                  <WifiOff className="size-3.5" />
                )}
                {health.data?.ready
                  ? "Backend ready"
                  : online
                    ? "Backend unavailable"
                    : "Browser offline"}
              </Badge>
              <p className="text-xs text-muted">
                {pendingCount + failedCount
                  ? `${pendingCount + failedCount} record${pendingCount + failedCount === 1 ? "" : "s"} awaiting sync`
                  : (health.data?.model_version ?? "Offline shell ready")}
              </p>
              {pendingCount + failedCount > 0 && (
                <button
                  className="text-xs font-bold text-teal underline"
                  disabled={!online || syncing}
                  onClick={() => void syncNow()}
                >
                  {syncing ? "Synchronizing…" : "Sync now"}
                </button>
              )}
            </div>
          )}
        </div>
      </aside>

      <MobileNavigation
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
      />

      <div
        className={`min-h-screen transition-[margin] ${collapsed ? "lg:ml-20" : "lg:ml-64"}`}
      >
        <header className="sticky top-0 z-30 flex min-h-16 items-center gap-3 border-b border-line bg-white/85 px-4 backdrop-blur-xl md:px-7">
          <button
            className="icon-button lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <Menu className="size-5" />
          </button>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-bold uppercase tracking-[.14em] text-teal">
              MundaSense AI <span aria-hidden="true">/</span>{" "}
              {location.pathname === "/" ? "Welcome" : "Workspace"}
            </p>
            <h1 className="truncate text-lg font-extrabold text-ink">
              {pageTitle}
            </h1>
          </div>
          <div className="hidden items-center gap-2 sm:flex">
            <Languages className="size-4 text-muted" aria-hidden="true" />
            <label className="sr-only" htmlFor="language">
              Language
            </label>
            <select
              id="language"
              className="input min-h-10 w-auto py-1"
              value={locale}
              onChange={(event) => setLocale(event.target.value as "en" | "sn")}
            >
              <option value="en">English</option>
              <option value="sn">Shona · demo</option>
            </select>
          </div>
          <div
            className="hidden rounded-xl border border-line bg-pale p-1 md:flex"
            aria-label="Interface mode"
          >
            <button
              onClick={() => setMode("farmer")}
              className={`min-h-9 rounded-lg px-3 text-xs font-bold ${mode === "farmer" ? "bg-white text-deep shadow-sm" : "text-muted"}`}
            >
              {translate(locale, "mode.farmer")}
            </button>
            <button
              onClick={() => setMode("officer")}
              className={`min-h-9 rounded-lg px-3 text-xs font-bold ${mode === "officer" ? "bg-white text-deep shadow-sm" : "text-muted"}`}
            >
              {translate(locale, "mode.officer")}
            </button>
          </div>
          <button
            className="button button-ghost hidden lg:inline-flex"
            onClick={() => void syncNow()}
            disabled={!online || syncing || pendingCount + failedCount === 0}
            title="Synchronize offline records"
          >
            <Cloud className="size-4" />
            <span>{pendingCount + failedCount}</span>
            {syncing && <RefreshCw className="size-3 animate-spin" />}
          </button>
          <NavLink
            to="/assess/new"
            className="button button-primary hidden xl:inline-flex"
          >
            <Plus className="size-4" />
            New assessment
          </NavLink>
        </header>
        {!online && (
          <div
            className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm font-semibold text-amber-900"
            role="status"
          >
            Offline mode — drafts and new records stay on this device;
            predictions wait for the local backend.
          </div>
        )}
        {online && !health.data?.ready && !health.isLoading && (
          <div
            className="border-b border-red-200 bg-red-50 px-4 py-2 text-center text-sm font-semibold text-red-800"
            role="alert"
          >
            Local backend unavailable — new assessments will be queued without a
            prediction.
          </div>
        )}
        <main
          id="main-content"
          className="mx-auto w-full max-w-[1440px] px-4 pb-24 pt-6 sm:px-6 lg:px-8 lg:pb-10"
        >
          <Outlet />
        </main>
      </div>

      <nav
        aria-label="Quick navigation"
        className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-4 border-t border-line bg-white/95 px-2 pb-[max(.35rem,env(safe-area-inset-bottom))] pt-1 backdrop-blur lg:hidden"
      >
        {[
          ["/", Home, "Home"],
          ["/assess/new", Plus, "Assess"],
          ["/history", History, "History"],
          ["/dashboard", Activity, "Dashboard"],
        ].map(([href, Icon, label]) => (
          <NavLink
            key={href as string}
            to={href as string}
            end={href === "/"}
            className={({ isActive }) =>
              `grid min-h-14 place-items-center rounded-lg text-[.68rem] font-bold ${isActive ? "text-deep" : "text-muted"}`
            }
          >
            <Icon className="size-5" />
            <span>{label as string}</span>
          </NavLink>
        ))}
      </nav>
      <ServiceWorkerUpdate />
    </div>
  );
}
