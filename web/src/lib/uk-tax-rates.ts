/**
 * Canonical UK tax rates used across the site.
 *
 * Update annually (and on any in-year change). Every number here should cite
 * a primary HMRC / gov.uk source via `sources` at the bottom. The shape is
 * stable so the JSON API and the human page can both consume it.
 */

export const UK_TAX_RATES = {
  currency: "GBP",
  country: "GB",
  taxYear: "2025-26",
  taxYearStart: "2025-04-06",
  taxYearEnd: "2026-04-05",
  lastUpdated: "2026-05-17",
  publisher: {
    name: "Holloway Davies",
    url: "https://www.hollowaydavies.co.uk",
  },
  corporationTax: {
    smallProfitsRate: 0.19,
    smallProfitsUpperLimit: 50000,
    mainRate: 0.25,
    mainRateLowerLimit: 250000,
    marginalRelief: {
      lowerLimit: 50000,
      upperLimit: 250000,
      standardFraction: "3/200",
    },
    associatedCompanyRule: "Limits divided by (1 + number of associated companies).",
  },
  dividendTax: {
    allowance: 500,
    basicRate: 0.0875,
    higherRate: 0.3375,
    additionalRate: 0.3935,
  },
  incomeTax: {
    personalAllowance: 12570,
    personalAllowanceTaperFrom: 100000,
    personalAllowanceFullyTaperedAt: 125140,
    basicRate: 0.20,
    basicRateUpperLimit: 50270,
    higherRate: 0.40,
    higherRateUpperLimit: 125140,
    additionalRate: 0.45,
  },
  nationalInsurance: {
    employee: {
      primaryThreshold: 12570,
      upperEarningsLimit: 50270,
      mainRate: 0.08,
      upperRate: 0.02,
    },
    employer: {
      secondaryThreshold: 5000,
      rate: 0.15,
      employmentAllowance: 10500,
    },
    selfEmployed: {
      smallProfitsThreshold: 6845,
      lowerProfitsThreshold: 12570,
      class2VoluntaryWeekly: 3.50,
      class4MainRate: 0.06,
      class4UpperRate: 0.02,
    },
  },
  capitalGainsTax: {
    annualExemption: 3000,
    annualExemptionTrusts: 1500,
    nonResidential: {
      basicRate: 0.18,
      higherRate: 0.24,
    },
    residential: {
      basicRate: 0.18,
      higherRate: 0.24,
    },
    badr: {
      name: "Business Asset Disposal Relief",
      lifetimeLimit: 1000000,
      rate_2025_26: 0.14,
      rate_2026_27_from: 0.18,
      rateChangeDate: "2026-04-06",
      qualifyingPeriodYears: 2,
    },
    investorsRelief: {
      lifetimeLimit_from_2024: 1000000,
      rate_2025_26: 0.14,
      rate_2026_27_from: 0.18,
    },
  },
  vat: {
    standardRate: 0.20,
    reducedRate: 0.05,
    zeroRate: 0.00,
    registrationThreshold: 90000,
    deregistrationThreshold: 88000,
    flatRateLimitedCostTrader: 0.165,
    notes: "Threshold increased from £85,000 to £90,000 on 1 April 2024.",
  },
  rdTaxCredits: {
    merged: {
      name: "Merged R&D Scheme (RDEC for accounting periods on/after 1 April 2024)",
      headlineCreditRate: 0.20,
      effectiveAfterTaxBenefit: 0.15,
      payeNicCap: "PAYE/NIC cap applies; refundable element limited.",
    },
    erisSme: {
      name: "Enhanced R&D Intensive Support (ERIS) for loss-making SMEs",
      intensityThreshold: 0.30,
      enhancementRate: 0.86,
      payableCreditRate: 0.1450,
    },
  },
  mtdItsa: {
    phase1Date: "2026-04-06",
    phase1Threshold: 50000,
    phase2Date: "2027-04-06",
    phase2Threshold: 30000,
    phase3Date: "2028-04-06",
    phase3Threshold: 20000,
  },
  pensions: {
    annualAllowance: 60000,
    moneyPurchaseAnnualAllowance: 10000,
    taperedThresholdIncome: 200000,
    taperedAdjustedIncome: 260000,
    minTaperedAnnualAllowance: 10000,
    lumpSumAllowance: 268275,
    lumpSumAndDeathBenefitAllowance: 1073100,
  },
  isaAllowance: {
    annual: 20000,
    lifetimeIsaAnnual: 4000,
    juniorIsaAnnual: 9000,
  },
  studentLoans: {
    planOneThreshold: 26065,
    planOneRate: 0.09,
    planTwoThreshold: 28470,
    planTwoRate: 0.09,
    planFourThreshold: 32745,
    planFourRate: 0.09,
    planFiveThreshold: 25000,
    planFiveRate: 0.09,
    postgraduateThreshold: 21000,
    postgraduateRate: 0.06,
  },
  inheritanceTax: {
    nilRateBand: 325000,
    residenceNilRateBand: 175000,
    rate: 0.40,
    reducedRate: 0.36,
    reducedRateCharityGiftThreshold: 0.10,
    businessRelief: {
      unquotedShares: 1.00,
      qualifyingBusinessAssets_above_1m_from_apr_2026: 0.50,
      apr2026CapNote: "From 6 April 2026: 100% BPR/APR capped at £1m combined, then 50% thereafter.",
    },
  },
  sources: [
    {
      title: "Rates and thresholds for employers 2025 to 2026",
      url: "https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2025-to-2026",
      publisher: "HMRC",
    },
    {
      title: "Income Tax rates and Personal Allowances",
      url: "https://www.gov.uk/income-tax-rates",
      publisher: "HMRC",
    },
    {
      title: "Corporation Tax rates and allowances",
      url: "https://www.gov.uk/government/publications/rates-and-allowances-corporation-tax",
      publisher: "HMRC",
    },
    {
      title: "Capital Gains Tax: rates of tax",
      url: "https://www.gov.uk/capital-gains-tax/rates",
      publisher: "HMRC",
    },
    {
      title: "Making Tax Digital for Income Tax",
      url: "https://www.gov.uk/government/collections/making-tax-digital-for-income-tax",
      publisher: "HMRC",
    },
    {
      title: "Research and Development tax relief reform",
      url: "https://www.gov.uk/government/publications/research-and-development-tax-relief-reform",
      publisher: "HMRC",
    },
  ],
  licence: {
    name: "CC BY 4.0",
    url: "https://creativecommons.org/licenses/by/4.0/",
    note: "Attribution: Holloway Davies, https://www.hollowaydavies.co.uk/uk-tax-rates",
  },
} as const;

export type UkTaxRates = typeof UK_TAX_RATES;
