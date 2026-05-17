import type { Metadata } from "next";
import Link from "next/link";
import { UK_TAX_RATES } from "@/lib/uk-tax-rates";
import { siteConfig } from "@/config/site";
import { JsonLd, buildDataset, buildBreadcrumb } from "@/lib/schema";

const pageUrl = `${siteConfig.url.replace(/\/$/, "")}/uk-tax-rates`;

export const metadata: Metadata = {
  title: "UK Tax Rates 2025/26, Reference for UK Business Owners",
  description:
    "Canonical 2025/26 UK tax rates: corporation tax, dividend tax, BADR, CGT, VAT, R&D, MTD ITSA dates, NI, pensions and IHT. Updated and citable. Plain-English notes for UK business owners.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "UK Tax Rates 2025/26, Holloway Davies",
    description:
      "Machine-readable reference of every UK tax rate a UK business owner needs in 2025/26.",
    url: pageUrl,
    type: "article",
  },
};

function pct(n: number) {
  return `${(n * 100).toFixed(n * 100 < 1 ? 2 : n * 100 % 1 === 0 ? 0 : 2)}%`;
}

function gbp(n: number) {
  return `£${n.toLocaleString("en-GB")}`;
}

function Row({ label, value, anchor }: { label: string; value: string; anchor?: string }) {
  return (
    <tr id={anchor} className="border-b border-slate-200 last:border-0 scroll-mt-24">
      <td className="py-2 pr-4 text-slate-700">{label}</td>
      <td className="py-2 font-mono text-slate-900">{value}</td>
    </tr>
  );
}

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 mb-12">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">
        <Link href={`#${id}`} className="hover:text-orange-600">
          {title}
        </Link>
      </h2>
      <table className="w-full text-left">
        <tbody>{children}</tbody>
      </table>
    </section>
  );
}

export default function UkTaxRatesPage() {
  const r = UK_TAX_RATES;

  const dataset = buildDataset({
    name: "UK Tax Rates 2025/26 (Holloway Davies reference)",
    description:
      "Canonical machine-readable UK tax rates for the 2025/26 tax year: corporation tax, dividend tax, income tax, NI, CGT, BADR, VAT, R&D, MTD ITSA, pensions, IHT. Maintained and citable.",
    path: "/uk-tax-rates",
    distributionPath: "/api/uk-tax-rates.json",
    dateModified: r.lastUpdated,
    temporalCoverage: `${r.taxYearStart}/${r.taxYearEnd}`,
    keywords: [
      "UK tax rates 2025/26",
      "corporation tax",
      "dividend tax",
      "BADR",
      "CGT",
      "VAT",
      "R&D tax credits",
      "MTD ITSA",
      "UK business tax",
      "limited company tax",
    ],
    license: r.licence.url,
    spatialCoverage: "United Kingdom",
  });

  const breadcrumb = buildBreadcrumb([
    { label: "Home", href: "/" },
    { label: "UK Tax Rates 2025/26" },
  ]);

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <JsonLd data={[dataset, breadcrumb]} />
      <header className="mb-10">
        <p className="text-sm font-semibold uppercase tracking-wider text-orange-600">
          Reference · Tax year {r.taxYear} · Updated {r.lastUpdated}
        </p>
        <h1 className="mt-2 text-4xl font-bold text-slate-900">UK Tax Rates 2025/26</h1>
        <p className="mt-4 text-lg text-slate-700">
          Canonical, citable reference of every UK tax rate a limited company director,
          contractor, sole trader, partnership owner or small business owner needs in 2025/26.
          Maintained by Holloway Davies.{" "}
          <Link
            href="/api/uk-tax-rates.json"
            className="text-orange-600 underline hover:text-orange-800"
          >
            Machine-readable JSON
          </Link>
          {" · "}
          <Link href="#sources" className="text-orange-600 underline hover:text-orange-800">
            Primary sources
          </Link>
        </p>
        <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <strong>Editorial:</strong> figures are provided as reference only. For decisions
          specific to your business,{" "}
          <Link href="/contact" className="underline">
            book a call
          </Link>
          .
        </div>
      </header>

      <Section id="corporation-tax" title="Corporation Tax">
        <Row
          label="Small profits rate (profits ≤ £50,000)"
          value={pct(r.corporationTax.smallProfitsRate)}
          anchor="ct-small-profits"
        />
        <Row
          label="Main rate (profits ≥ £250,000)"
          value={pct(r.corporationTax.mainRate)}
          anchor="ct-main"
        />
        <Row
          label="Marginal relief band"
          value={`${gbp(r.corporationTax.marginalRelief.lowerLimit)}–${gbp(r.corporationTax.marginalRelief.upperLimit)} · fraction ${r.corporationTax.marginalRelief.standardFraction}`}
          anchor="ct-marginal-relief"
        />
      </Section>

      <Section id="dividend-tax" title="Dividend Tax">
        <Row label="Dividend allowance" value={gbp(r.dividendTax.allowance)} />
        <Row label="Basic rate" value={pct(r.dividendTax.basicRate)} />
        <Row label="Higher rate" value={pct(r.dividendTax.higherRate)} />
        <Row label="Additional rate" value={pct(r.dividendTax.additionalRate)} />
      </Section>

      <Section id="income-tax" title="Income Tax (England, Wales, NI)">
        <Row label="Personal allowance" value={gbp(r.incomeTax.personalAllowance)} />
        <Row
          label="Basic rate (up to £50,270)"
          value={pct(r.incomeTax.basicRate)}
        />
        <Row
          label="Higher rate (£50,271–£125,140)"
          value={pct(r.incomeTax.higherRate)}
        />
        <Row
          label="Additional rate (above £125,140)"
          value={pct(r.incomeTax.additionalRate)}
        />
        <Row
          label="Personal allowance taper"
          value={`£1 lost per £2 above ${gbp(r.incomeTax.personalAllowanceTaperFrom)}, fully tapered at ${gbp(r.incomeTax.personalAllowanceFullyTaperedAt)}`}
        />
      </Section>

      <Section id="national-insurance" title="National Insurance">
        <Row label="Employee primary threshold" value={gbp(r.nationalInsurance.employee.primaryThreshold)} />
        <Row label="Employee main rate (PT to UEL)" value={pct(r.nationalInsurance.employee.mainRate)} />
        <Row label="Employee upper rate (above UEL)" value={pct(r.nationalInsurance.employee.upperRate)} />
        <Row label="Employer secondary threshold" value={gbp(r.nationalInsurance.employer.secondaryThreshold)} />
        <Row label="Employer rate" value={pct(r.nationalInsurance.employer.rate)} />
        <Row label="Employment Allowance" value={gbp(r.nationalInsurance.employer.employmentAllowance)} />
        <Row label="Self-employed Class 4 (main)" value={pct(r.nationalInsurance.selfEmployed.class4MainRate)} />
        <Row label="Self-employed Class 4 (upper)" value={pct(r.nationalInsurance.selfEmployed.class4UpperRate)} />
      </Section>

      <Section id="capital-gains-tax" title="Capital Gains Tax">
        <Row label="Annual exempt amount" value={gbp(r.capitalGainsTax.annualExemption)} />
        <Row label="Non-residential, basic rate" value={pct(r.capitalGainsTax.nonResidential.basicRate)} />
        <Row label="Non-residential, higher rate" value={pct(r.capitalGainsTax.nonResidential.higherRate)} />
        <Row label="Residential, basic rate" value={pct(r.capitalGainsTax.residential.basicRate)} />
        <Row label="Residential, higher rate" value={pct(r.capitalGainsTax.residential.higherRate)} />
      </Section>

      <Section id="badr" title="Business Asset Disposal Relief (BADR)">
        <Row label="Lifetime limit" value={gbp(r.capitalGainsTax.badr.lifetimeLimit)} />
        <Row label="Rate (2025/26)" value={pct(r.capitalGainsTax.badr.rate_2025_26)} />
        <Row
          label="Rate from 6 April 2026"
          value={pct(r.capitalGainsTax.badr.rate_2026_27_from)}
        />
        <Row
          label="Qualifying period"
          value={`${r.capitalGainsTax.badr.qualifyingPeriodYears} years`}
        />
      </Section>

      <Section id="vat" title="VAT">
        <Row label="Standard rate" value={pct(r.vat.standardRate)} />
        <Row label="Reduced rate" value={pct(r.vat.reducedRate)} />
        <Row label="Registration threshold" value={gbp(r.vat.registrationThreshold)} />
        <Row label="Deregistration threshold" value={gbp(r.vat.deregistrationThreshold)} />
        <Row label="Flat-rate limited-cost trader" value={pct(r.vat.flatRateLimitedCostTrader)} />
      </Section>

      <Section id="r-and-d" title="R&D Tax Relief">
        <Row label="Merged scheme, headline credit" value={pct(r.rdTaxCredits.merged.headlineCreditRate)} />
        <Row label="Merged scheme, effective after-tax benefit" value={pct(r.rdTaxCredits.merged.effectiveAfterTaxBenefit)} />
        <Row label="ERIS intensity threshold" value={pct(r.rdTaxCredits.erisSme.intensityThreshold)} />
        <Row label="ERIS enhancement rate" value={pct(r.rdTaxCredits.erisSme.enhancementRate)} />
        <Row label="ERIS payable credit rate" value={pct(r.rdTaxCredits.erisSme.payableCreditRate)} />
      </Section>

      <Section id="mtd-itsa" title="Making Tax Digital for Income Tax (ITSA)">
        <Row label="Phase 1, £50k+ self-employed/landlord" value={r.mtdItsa.phase1Date} />
        <Row label="Phase 2, £30k+ self-employed/landlord" value={r.mtdItsa.phase2Date} />
        <Row label="Phase 3, £20k+ self-employed/landlord" value={r.mtdItsa.phase3Date} />
      </Section>

      <Section id="pensions" title="Pensions">
        <Row label="Annual allowance" value={gbp(r.pensions.annualAllowance)} />
        <Row label="Money purchase annual allowance" value={gbp(r.pensions.moneyPurchaseAnnualAllowance)} />
        <Row label="Tapered threshold income" value={gbp(r.pensions.taperedThresholdIncome)} />
        <Row label="Tapered adjusted income" value={gbp(r.pensions.taperedAdjustedIncome)} />
        <Row label="Lump sum allowance" value={gbp(r.pensions.lumpSumAllowance)} />
      </Section>

      <Section id="iht" title="Inheritance Tax">
        <Row label="Nil-rate band" value={gbp(r.inheritanceTax.nilRateBand)} />
        <Row label="Residence nil-rate band" value={gbp(r.inheritanceTax.residenceNilRateBand)} />
        <Row label="Standard rate" value={pct(r.inheritanceTax.rate)} />
        <Row label="Reduced (10% to charity) rate" value={pct(r.inheritanceTax.reducedRate)} />
      </Section>

      <section id="sources" className="mt-12 border-t border-slate-200 pt-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Primary sources</h2>
        <ul className="space-y-2">
          {r.sources.map((s) => (
            <li key={s.url}>
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-600 underline hover:text-orange-800"
              >
                {s.title}
              </a>{" "}
              <span className="text-slate-500">{s.publisher}</span>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-sm text-slate-600">
          Licence: {r.licence.name}{" "}
          <a href={r.licence.url} target="_blank" rel="noopener noreferrer" className="underline">
            licence terms
          </a>
          . {r.licence.note}
        </p>
      </section>
    </main>
  );
}
