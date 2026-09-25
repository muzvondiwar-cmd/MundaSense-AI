import type { Locale } from "../types/api";

export const en = {
  "nav.home": "Home",
  "nav.assess": "New assessment",
  "nav.scenario": "Scenario Lab",
  "nav.dashboard": "Officer dashboard",
  "nav.history": "History",
  "nav.model": "Model card",
  "nav.about": "About & safety",
  "action.start": "Start maize assessment",
  "action.demo": "Open demo scenario",
  "status.ready": "Local system ready",
  "status.offline": "Backend unavailable",
  "mode.farmer": "Farmer",
  "mode.officer": "Extension Officer",
  "common.synthetic": "Synthetic demo data",
  "common.retry": "Try again",
  "common.loading": "Loading local data",
  "risk.low": "Low yield risk",
  "risk.moderate": "Moderate yield risk",
  "risk.high": "High yield risk",
  "confidence.high": "High confidence",
  "confidence.medium": "Medium confidence",
  "confidence.low": "Low confidence",
  "confidence.insufficient": "Insufficient basis",
} as const;

type TranslationKey = keyof typeof en;

const sn: Partial<Record<TranslationKey, string>> = {
  "nav.home": "Kumba",
  "nav.assess": "Ongororo itsva",
  "nav.history": "Nhoroondo yeongororo",
  "nav.model": "Kuongorora modhi",
  "nav.about": "Nezve chirongwa nekuchengeteka",
  "action.start": "Tanga ongororo yemunda",
  "risk.low": "Njodzi yegoho yakaderera",
  "risk.moderate": "Njodzi yegoho iri pakati",
  "risk.high": "Njodzi yegoho yakakwirira",
  "confidence.high": "Kuvimba kwakakwirira",
  "confidence.medium": "Kuvimba kuri pakati",
  "confidence.low": "Kuvimba kwakaderera",
  "confidence.insufficient": "Humbowo hahuna kukwana",
};

export function translate(locale: Locale, key: TranslationKey): string {
  return locale === "sn" ? (sn[key] ?? en[key]) : en[key];
}

export type { TranslationKey };
