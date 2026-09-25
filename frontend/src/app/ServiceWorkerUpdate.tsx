import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

export function ServiceWorkerUpdate() {
  const [waiting, setWaiting] = useState<ServiceWorker | null>(null);

  useEffect(() => {
    if (!("serviceWorker" in navigator) || !import.meta.env.PROD) return;
    let refreshing = false;
    const reload = () => {
      if (refreshing) return;
      refreshing = true;
      window.location.reload();
    };
    navigator.serviceWorker.addEventListener("controllerchange", reload);
    void navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        if (registration.waiting) setWaiting(registration.waiting);
        registration.addEventListener("updatefound", () => {
          const worker = registration.installing;
          worker?.addEventListener("statechange", () => {
            if (
              worker.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              setWaiting(worker);
            }
          });
        });
        void registration.update();
      })
      .catch(() => undefined);
    return () =>
      navigator.serviceWorker.removeEventListener("controllerchange", reload);
  }, []);

  if (!waiting) return null;
  return (
    <div
      className="fixed bottom-20 left-4 right-4 z-[90] mx-auto flex max-w-xl items-center justify-between gap-3 rounded-2xl border border-green-300 bg-white p-4 shadow-2xl lg:bottom-5"
      role="status"
    >
      <div>
        <p className="font-extrabold text-ink">MundaSense update available</p>
        <p className="text-sm text-muted">
          Reload when ready to use the latest local interface.
        </p>
      </div>
      <button
        className="button button-primary shrink-0"
        onClick={() => waiting.postMessage({ type: "SKIP_WAITING" })}
      >
        <RefreshCw className="size-4" />
        Update now
      </button>
    </div>
  );
}
