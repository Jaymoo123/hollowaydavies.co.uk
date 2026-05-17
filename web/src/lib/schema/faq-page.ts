import type { SchemaThing } from "./types";

export type FaqEntry = { question: string; answer: string };

/**
 * FAQPage with a mainEntity Question/Answer pair list. Pass anywhere the
 * page has a Q&A section. AI engines and Google use this for direct-answer
 * surfaces.
 */
export function buildFaqPage(faqs: FaqEntry[]): SchemaThing | null {
  if (!faqs || faqs.length === 0) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: f.answer,
      },
    })),
  };
}
