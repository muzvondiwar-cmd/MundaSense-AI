import { CheckCircle2, X } from "lucide-react";
import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

interface ToastItem {
  id: number;
  message: string;
}

const ToastContext = createContext<{
  notify: (message: string) => void;
} | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const value = useMemo(
    () => ({
      notify: (message: string) => {
        const id = Date.now();
        setItems((current) => [...current, { id, message }]);
        window.setTimeout(
          () => setItems((current) => current.filter((item) => item.id !== id)),
          3500,
        );
      },
    }),
    [],
  );
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="fixed right-4 top-4 z-[80] grid gap-2"
        aria-live="polite"
        aria-atomic="true"
      >
        {items.map((item) => (
          <div
            key={item.id}
            className="flex min-w-72 items-center gap-3 rounded-xl border border-green-200 bg-white px-4 py-3 shadow-xl"
          >
            <CheckCircle2
              className="size-5 text-green-700"
              aria-hidden="true"
            />
            <span className="flex-1 text-sm font-semibold text-ink">
              {item.message}
            </span>
            <button
              className="icon-button"
              onClick={() =>
                setItems((current) =>
                  current.filter((entry) => entry.id !== item.id),
                )
              }
              aria-label="Dismiss notification"
            >
              <X className="size-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const value = useContext(ToastContext);
  if (!value) throw new Error("useToast must be used inside ToastProvider");
  return value;
}
