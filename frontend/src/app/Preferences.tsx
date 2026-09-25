import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import type { Locale } from "../types/api";

type UserMode = "farmer" | "officer";

interface PreferencesValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  mode: UserMode;
  setMode: (mode: UserMode) => void;
}

const PreferencesContext = createContext<PreferencesValue | null>(null);

function stored<T extends string>(key: string, legacyKey: string, fallback: T): T {
  return (
    (window.localStorage.getItem(key) as T | null) ??
    (window.localStorage.getItem(legacyKey) as T | null) ??
    fallback
  );
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [localeState, setLocaleState] = useState<Locale>(() =>
    stored("mundasense.v1.locale", "mundasense.locale", "en"),
  );
  const [modeState, setModeState] = useState<UserMode>(() =>
    stored("mundasense.v1.mode", "mundasense.mode", "farmer"),
  );
  useEffect(() => {
    document.documentElement.lang = localeState;
  }, [localeState]);
  const value = useMemo(
    () => ({
      locale: localeState,
      setLocale: (locale: Locale) => {
        window.localStorage.setItem("mundasense.v1.locale", locale);
        setLocaleState(locale);
      },
      mode: modeState,
      setMode: (mode: UserMode) => {
        window.localStorage.setItem("mundasense.v1.mode", mode);
        setModeState(mode);
      },
    }),
    [localeState, modeState],
  );
  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences(): PreferencesValue {
  const value = useContext(PreferencesContext);
  if (!value) throw new Error("usePreferences must be used inside PreferencesProvider");
  return value;
}
