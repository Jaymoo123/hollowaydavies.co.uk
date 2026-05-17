/** Layout utility tokens. Centralised so every page composes from the same vocabulary. */

export const siteContainer =
  "mx-auto w-full max-w-5xl px-4 sm:px-6 lg:px-8 min-w-0";

export const siteContainerLg =
  "mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8 min-w-0";

export const contentNarrow =
  "mx-auto w-full max-w-3xl px-4 sm:px-6 lg:px-8 min-w-0";

/** Generous vertical rhythm. Sections breathe. */
export const sectionY = "py-16 sm:py-20 lg:py-28";

export const sectionYLoose = "py-20 sm:py-28 lg:py-36";

export const focusRing =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500";

/** Primary CTA: flat orange, no shadows, sharp corners, darkens on hover. */
export const btnPrimary =
  "inline-flex min-h-12 items-center justify-center bg-orange-500 px-7 py-3.5 text-sm font-medium text-white tracking-wide transition-colors duration-150 hover:bg-orange-600 active:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500";

/** Dark CTA: for use on orange / warm backgrounds where orange-on-orange would lack contrast. */
export const btnOnOrange =
  "inline-flex min-h-12 items-center justify-center bg-slate-900 px-7 py-3.5 text-sm font-medium text-white tracking-wide transition-colors duration-150 hover:bg-black active:bg-black disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white";

/** Secondary CTA: outlined ink-on-offwhite. Fills with ink on hover. */
export const btnSecondary =
  "inline-flex min-h-12 items-center justify-center border border-neutral-900 bg-transparent px-7 py-3.5 text-sm font-medium text-neutral-900 tracking-wide transition-colors duration-150 hover:bg-neutral-900 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500";

/** Inline text link with arrow. For low-emphasis secondary actions. */
export const linkArrow =
  "inline-flex items-center gap-1.5 text-sm font-medium text-neutral-900 transition-opacity hover:opacity-70 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-orange-500";

/** Legacy export kept so any inherited components that still import btnOnDark
 * compile while Phase B rewrites them. Visually neutral; do not use in new code. */
export const btnOnDark = btnSecondary;
