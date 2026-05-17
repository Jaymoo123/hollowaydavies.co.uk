import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getTeamMember, getAllTeamSlugs } from "./data";
import { siteConfig } from "@/config/site";
import { JsonLd, buildPerson, buildBreadcrumb } from "@/lib/schema";

export const dynamicParams = false;

export async function generateStaticParams() {
  return getAllTeamSlugs().map((slug) => ({ slug }));
}

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const m = getTeamMember(slug);
  if (!m) return {};
  const url = `${siteConfig.url.replace(/\/$/, "")}/team/${m.slug}`;
  return {
    title: `${m.name}, ${m.role}`,
    description: m.shortBio,
    alternates: { canonical: url },
    openGraph: {
      type: "profile",
      title: `${m.name}, ${m.role}`,
      description: m.shortBio,
      url,
    },
  };
}

function Monogram({ initials, color }: { initials: string; color: string }) {
  return (
    <svg
      viewBox="0 0 96 96"
      width="96"
      height="96"
      role="img"
      aria-label={`${initials} monogram`}
      className="rounded-full"
    >
      <rect width="96" height="96" rx="48" fill={color} />
      <text
        x="50%"
        y="54%"
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="Inter, system-ui, sans-serif"
        fontSize="36"
        fontWeight="700"
        fill="#ffffff"
      >
        {initials}
      </text>
    </svg>
  );
}

export default async function TeamMemberPage({ params }: Props) {
  const { slug } = await params;
  const m = getTeamMember(slug);
  if (!m) notFound();

  const person = buildPerson(m.slug);
  const breadcrumb = buildBreadcrumb([
    { label: "Home", href: "/" },
    { label: "Team" },
    { label: m.name },
  ]);

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <JsonLd data={person ? [person, breadcrumb] : [breadcrumb]} />
      <nav aria-label="Breadcrumb" className="mb-6 text-sm text-slate-600">
        <Link href="/" className="hover:text-orange-600">
          Home
        </Link>{" "}
        / <span>Team</span> /{" "}
        <span className="text-slate-900">{m.name}</span>
      </nav>

      <header className="flex items-start gap-6 mb-8">
        <Monogram initials={m.initials} color={m.monogramColor} />
        <div>
          <h1 className="text-3xl font-bold text-slate-900">{m.name}</h1>
          <p className="mt-1 text-lg text-slate-700">{m.role}</p>
          <p className="mt-1 text-sm text-slate-500">
            {siteConfig.name}
          </p>
        </div>
      </header>

      <div className="prose prose-slate max-w-none">
        {m.bio.map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>

      <section className="mt-10 border-t border-slate-200 pt-8">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Areas of focus</h2>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {m.expertise.map((e) => (
            <li key={e} className="text-slate-700">
              · {e}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
        <strong>Editorial disclosure:</strong> articles on this site are editorial
        content written and reviewed by the {siteConfig.name} team. They are
        not personalised tax advice. For decisions specific to your business,{" "}
        <Link href="/contact" className="underline">
          book a call
        </Link>
        .
      </section>
    </main>
  );
}
