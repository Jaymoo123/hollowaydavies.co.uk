import { siteConfig } from "@/config/site";
import { referencedOrganization } from "./organization";
import type { SchemaThing } from "./types";

export type DatasetInput = {
  name: string;
  description: string;
  /** Path of the human page */
  path: string;
  /** Path of the machine-readable distribution (e.g. /api/uk-tax-rates.json) */
  distributionPath?: string;
  /** ISO date string of last update */
  dateModified: string;
  /** Optional ISO temporal coverage range e.g. "2025-04-06/2026-04-05" */
  temporalCoverage?: string;
  keywords?: string[];
  /** License URL (e.g. CC BY 4.0) */
  license?: string;
  /** Country covered */
  spatialCoverage?: string;
};

/**
 * Dataset schema for pages that publish citable primary data.
 * Used by /uk-tax-rates and any future benchmark pages.
 */
export function buildDataset(input: DatasetInput): SchemaThing {
  const url = `${siteConfig.url}${input.path}`;
  const out: SchemaThing = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    "@id": `${url}#dataset`,
    name: input.name,
    description: input.description,
    url,
    creator: referencedOrganization(),
    publisher: referencedOrganization(),
    dateModified: input.dateModified,
    isAccessibleForFree: true,
    inLanguage: "en-GB",
    ...(input.keywords && input.keywords.length ? { keywords: input.keywords } : {}),
    ...(input.license ? { license: input.license } : {}),
    ...(input.temporalCoverage ? { temporalCoverage: input.temporalCoverage } : {}),
    ...(input.spatialCoverage
      ? {
          spatialCoverage: {
            "@type": "Country",
            name: input.spatialCoverage,
          },
        }
      : {}),
  };

  if (input.distributionPath) {
    out.distribution = [
      {
        "@type": "DataDownload",
        encodingFormat: "application/json",
        contentUrl: `${siteConfig.url}${input.distributionPath}`,
      },
    ];
  }

  return out;
}
