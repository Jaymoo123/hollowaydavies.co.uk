import { siteConfig } from "@/config/site";
import type { SchemaThing } from "./types";

export type HowToStep = {
  name: string;
  text: string;
  /** Optional URL to a specific section */
  url?: string;
};

export type HowToInput = {
  name: string;
  description: string;
  path: string;
  steps: HowToStep[];
  /** Total time, ISO 8601 e.g. "PT5M" */
  totalTime?: string;
};

/**
 * HowTo schema for step-by-step pages. Useful for calculator usage guides
 * or "how to claim X" walkthroughs.
 */
export function buildHowTo(input: HowToInput): SchemaThing {
  const url = `${siteConfig.url}${input.path}`;
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "@id": `${url}#howto`,
    name: input.name,
    description: input.description,
    url,
    inLanguage: "en-GB",
    step: input.steps.map((s, i) => ({
      "@type": "HowToStep",
      position: i + 1,
      name: s.name,
      text: s.text,
      ...(s.url ? { url: s.url } : {}),
    })),
    ...(input.totalTime ? { totalTime: input.totalTime } : {}),
  };
}
