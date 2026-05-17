/**
 * Welcome series content. Five emails spaced over ~14 days after double opt-in.
 *
 * Tone: FT-editorial peer-to-peer, plain-text-feel, one CTA each.
 * Cadence (days after confirm): 0, 2, 5, 9, 14.
 *
 * Audience: UK business owners. Limited company directors, contractors,
 * sole traders, partnership owners, small business owners. Not founders
 * (per design system voice constraint).
 */

export type WelcomeStep = {
  step: number;
  delayHours: number; // hours after confirm before sending
  subject: string;
  preview: string;
  greeting: string;
  paragraphs: string[];
  ctaLabel: string;
  ctaUrl: string;
  sign: string;
};

const BASE = "https://www.hollowaydavies.co.uk";
const SIGN = "Emma, Holloway Davies";

export const WELCOME_SERIES: WelcomeStep[] = [
  {
    step: 1,
    delayHours: 0,
    subject: "You're in. What to expect from The Director's Brief.",
    preview: "Quick orientation, one calculator to try, one page worth bookmarking.",
    greeting: "Welcome to The Director's Brief.",
    paragraphs: [
      "You'll get one email a week, on a Thursday morning. Plain text, one tax or finance idea worth your time, no banner ads, no upsell.",
      "Two things to do right now.",
      "First, bookmark the 2025/26 UK tax rates page. It's the canonical reference we use internally for corporation tax, dividend tax, BADR, VAT, MTD ITSA dates, R&D rates, employer NI, everything. Updated when HMRC changes anything.",
      "Second, if you run a limited company and pay yourself a mix of salary and dividends, run the salary-dividend optimiser with your numbers. Most directors set the split once and never revisit it; the wrong split typically costs £2,000 to £6,000 a year for a director on £40k to £80k of total extraction.",
      "Next email Saturday-ish: the R&D claim mistake most UK companies make, and why the line moved in 2024.",
    ],
    ctaLabel: "Open the salary-dividend optimiser",
    ctaUrl: `${BASE}/calculators/salary-dividend-optimiser`,
    sign: SIGN,
  },
  {
    step: 2,
    delayHours: 48,
    subject: "The R&D claim mistake most UK companies make",
    preview: "Build vs research, and why the merged scheme is stricter.",
    greeting: "Quick one on R&D tax credits.",
    paragraphs: [
      "Companies that build something custom (software, AI tools, integrations, scientific processes, new manufacturing techniques, novel engineering) often assume the build itself is the R&D. It usually isn't.",
      "HMRC pays for the resolution of scientific or technological uncertainty: the specific bits where a competent professional in the field couldn't have predicted the outcome by reading the documentation. The bespoke build for a client is rarely that. The new technique you had to invent to make it work might be.",
      "The merged R&D scheme (accounting periods on or after 1 April 2024) tightened this further. Subcontractor R&D often shifts to the customer's claim, the headline rate dropped to 20%, and the Enhanced R&D Intensive Support scheme (ERIS) only applies to loss-making SMEs where R&D is at least 30% of total expenditure.",
      "If you have claimed before and the numbers feel rough, it is worth a 20-minute conversation. If you have never claimed, the eligibility page below covers the qualifying activity tests by sector.",
    ],
    ctaLabel: "R&D eligibility for UK companies",
    ctaUrl: `${BASE}/r-and-d-credits`,
    sign: SIGN,
  },
  {
    step: 3,
    delayHours: 120,
    subject: "Pillar guides: pick whichever is most relevant",
    preview: "Definitive long-form guides, in the order most directors and owners need them.",
    greeting: "If you only read one thing on the site this week.",
    paragraphs: [
      "We publish definitive pillar guides on the questions UK business owners ask most often. In rough order of who needs them:",
      "If you are deciding how to structure: Limited Company vs Sole Trader.",
      "If you are about to incorporate: How to Register a Limited Company UK.",
      "If you are a limited company director and want to extract money efficiently: How to Pay Yourself From a Limited Company.",
      "If corporation tax feels like a black box: How Does Corporation Tax Work.",
      "If you are a contractor: IR35 Explained.",
      "If MTD ITSA is on your radar (April 2026 for £50k+ self-employed and landlords): Making Tax Digital for Income Tax.",
      "If R&D is part of your business model: R&D Tax Credits Explained.",
      "If exit is anywhere on the horizon: Business Asset Disposal Relief Explained.",
      "If you are filing self assessment: Self Assessment Tax Return Guide.",
    ],
    ctaLabel: "Browse the pillar guides",
    ctaUrl: `${BASE}/fundamentals`,
    sign: SIGN,
  },
  {
    step: 4,
    delayHours: 216,
    subject: "MTD ITSA: what April 2026 actually requires",
    preview: "If your self-employment or rental income is over £50,000, this affects you.",
    greeting: "On MTD for Income Tax.",
    paragraphs: [
      "From 6 April 2026, Making Tax Digital for Income Tax Self Assessment (MTD ITSA) becomes mandatory for sole traders and landlords whose qualifying income is over £50,000 a year. From April 2027 it drops to £30,000. From April 2028, £20,000.",
      "What that actually means: you replace one annual self assessment return with four quarterly digital updates plus a final declaration. You must use HMRC-recognised software (Xero, FreeAgent, QuickBooks, GoSimpleTax and others) that keeps digital records and sends the data straight to HMRC. Spreadsheets only work with bridging software.",
      "If you cross the £50,000 threshold once in any tax year from 2024/25 onwards, you are in scope from the next April. So if your 2024/25 self assessment shows £52,000 of self-employment plus rental income combined, you are in scope from April 2026, no exceptions.",
      "The pillar guide below covers the timeline, what counts as qualifying income, the software shortlist and the practical setup steps. Worth a read now, not in March 2026.",
    ],
    ctaLabel: "MTD for Income Tax pillar guide",
    ctaUrl: `${BASE}/fundamentals/making-tax-digital-for-income-tax-guide`,
    sign: SIGN,
  },
  {
    step: 5,
    delayHours: 336,
    subject: "A free call: 60 minutes, your numbers, no sales pitch",
    preview: "If anything in the last two weeks raised a question worth a conversation.",
    greeting: "One last thing before the regular emails start.",
    paragraphs: [
      "If anything in the last two weeks has made you wonder whether you have the structure right (sole trader vs limited company), the salary/dividend split right, an R&D claim worth pursuing, an MTD ITSA timeline to plan, or any other UK tax or accounting question, you can book a free 60-minute call.",
      "It is on a video call, with an ICAEW qualified accountant on our team. You get a written summary by email afterwards with anything specific we would recommend. No sales pitch. About half the businesses we speak to we tell to stay with their current accountant and just change one thing.",
      "From here, the emails drop to one a week, Thursday morning, The Director's Brief. You can unsubscribe any time using the link at the bottom of every email.",
    ],
    ctaLabel: "Book a free call",
    ctaUrl: `${BASE}/contact`,
    sign: SIGN,
  },
];
