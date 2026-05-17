import { siteConfig } from "@/config/site";
import { referencedOrganization } from "./organization";
import type { SchemaThing } from "./types";

export type CourseInput = {
  name: string;
  description: string;
  /** Path of the pillar guide */
  path: string;
  /** Total time investment, ISO 8601 duration e.g. "PT30M" */
  timeRequired?: string;
};

/**
 * Course schema for Fundamentals pillar guides. Marks them as
 * learning resources distinct from generic articles, Google
 * surfaces these in education-flavoured panels.
 *
 * Use alongside `buildArticle` for the same page.
 */
export function buildCourse(input: CourseInput): SchemaThing {
  const url = `${siteConfig.url}${input.path}`;
  return {
    "@context": "https://schema.org",
    "@type": "Course",
    "@id": `${url}#course`,
    name: input.name,
    description: input.description,
    url,
    provider: referencedOrganization(),
    inLanguage: "en-GB",
    isAccessibleForFree: true,
    educationalLevel: "Professional",
    teaches: input.name,
    ...(input.timeRequired ? { timeRequired: input.timeRequired } : {}),
    hasCourseInstance: {
      "@type": "CourseInstance",
      courseMode: "online",
      courseWorkload: input.timeRequired || "PT30M",
    },
  };
}
