import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { Locale } from "../types/api";

type UserMode = "farmer" | "officer";
export type ThemePreference = "light" | "dark" | "system";

interface PreferencesValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  mode: UserMode;
  setMode: (mode: UserMode) => void;
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
  demoMode: boolean;
  setDemoMode: (enabled: boolean) => void;
}

const PreferencesContext = createContext<PreferencesValue | null>(null);

function stored<T extends string>(
  key: string,
  legacyKey: string,
  fallback: T,
): T {
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
  const [themeState, setThemeState] = useState<ThemePreference>(() =>
    stored("mundasense.v1.theme", "mundasense.theme", "system"),
  );
  const [demoModeState, setDemoModeState] = useState(
    () => window.localStorage.getItem("mundasense.v1.demo-mode") !== "false",
  );
  useEffect(() => {
    document.documentElement.lang = localeState;
  }, [localeState]);
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      document.documentElement.dataset.theme =
        themeState === "system"
          ? media.matches
            ? "dark"
            : "light"
          : themeState;
      document.documentElement.style.colorScheme =
        themeState === "system" ? "light dark" : themeState;
    };
    apply();
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, [themeState]);
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
      theme: themeState,
      setTheme: (theme: ThemePreference) => {
        window.localStorage.setItem("mundasense.v1.theme", theme);
        setThemeState(theme);
      },
      demoMode: demoModeState,
      setDemoMode: (enabled: boolean) => {
        window.localStorage.setItem("mundasense.v1.demo-mode", String(enabled));
        setDemoModeState(enabled);
      },
    }),
    [localeState, modeState, themeState, demoModeState],
  );
  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences(): PreferencesValue {
  const value = useContext(PreferencesContext);
  if (!value)
    throw new Error("usePreferences must be used inside PreferencesProvider");
  return value;
}
