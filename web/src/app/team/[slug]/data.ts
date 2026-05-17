/**
 * Editorial team / contributor data.
 *
 * Bylines here are editorial pen-names. Concrete tax advice is delivered
 * to clients via book-a-call, not via published content. Every page that
 * cites these authors carries an "editorial content, book a call for
 * advice" disclosure so readers are not misled into following content as
 * personalised guidance.
 */

export type TeamMember = {
  slug: string;
  name: string;
  initials: string;
  role: string;
  qualifications?: string;
  shortBio: string;
  bio: string[];
  expertise: string[];
  // Optional sameAs identities, fill when real profiles exist
  links?: { label: string; url: string }[];
  monogramColor: string;
};

export const TEAM: Record<string, TeamMember> = {
  "emma-carter": {
    slug: "emma-carter",
    name: "Emma Carter",
    initials: "EC",
    role: "Editorial Lead",
    shortBio:
      "Editorial lead at Holloway Davies. Writes on UK tax, incorporation, VAT, payroll and R&D credits for limited companies and sole traders.",
    bio: [
      "Emma Carter is the editorial lead at Holloway Davies. She writes and commissions content on UK corporation tax, VAT, payroll, R&D credits, incorporation decisions, and the practical accounting questions UK business owners actually ask.",
      "Editorial focus is plain-English explanation backed by primary sources. Every figure on this site is traceable back to HMRC, Companies House, or equivalent. Concrete advice for a specific business is delivered via a one-to-one call with a qualified accountant on the partner team, not via published articles.",
      "If something on the site is wrong, out of date, or unclear, get in touch and the editorial team will fix it.",
    ],
    expertise: [
      "UK corporation tax and marginal relief",
      "VAT registration and scheme selection",
      "Salary and dividend structuring",
      "R&D tax credits for UK SMEs",
      "Incorporation decisions and timing",
      "Making Tax Digital for ITSA",
    ],
    monogramColor: "#1e40af",
  },
  "james-holloway": {
    slug: "james-holloway",
    name: "James Holloway",
    initials: "JH",
    role: "Technical Reviewer",
    qualifications: "BSc Accounting and Finance, ICAEW Chartered Accountant",
    shortBio:
      "ICAEW Chartered Accountant. Technical reviewer on every published article. Specialist in UK corporation tax, BADR, R&D credits and exit planning.",
    bio: [
      "James Holloway is the technical reviewer on every article published by Holloway Davies. He qualified with ICAEW after a BSc in Accounting and Finance and has spent his career advising UK limited companies on corporation tax, share structure, R&D claims and exit strategy.",
      "Every piece of content on this site is reviewed against current HMRC and Companies House guidance before publication. Where figures, deadlines or rates change in the next Budget or Finance Act, the editorial team updates the article and republishes; James signs off the change.",
      "James does not publish personalised advice through articles. Tailored advice for a specific business is delivered via a one-to-one call with a qualified accountant on the partner team.",
    ],
    expertise: [
      "UK corporation tax including marginal relief and associated company rules",
      "Business Asset Disposal Relief (BADR) planning and CGT structuring",
      "R&D tax credits (RDEC and merged scheme)",
      "Exit planning, MVL vs strike-off, earn-out structures",
      "Director remuneration and dividend planning",
      "Holding company structures and group reorganisations",
    ],
    monogramColor: "#c2410c",
  },
};

export function getTeamMember(slug: string): TeamMember | null {
  return TEAM[slug] ?? null;
}

export function getAllTeamSlugs(): string[] {
  return Object.keys(TEAM);
}
