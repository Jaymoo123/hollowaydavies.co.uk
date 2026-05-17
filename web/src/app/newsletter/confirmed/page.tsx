import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Subscription confirmed | Holloway Davies",
  robots: { index: false, follow: false },
};

type Props = { searchParams: Promise<{ error?: string }> };

export default async function ConfirmedPage({ searchParams }: Props) {
  const { error } = await searchParams;

  if (error) {
    const message =
      error === "expired"
        ? "That confirmation link has expired. Please subscribe again."
        : error === "bad-signature" || error === "malformed"
          ? "That confirmation link looks invalid. Please subscribe again."
          : "Something went wrong confirming your subscription.";
    return (
      <main className="mx-auto max-w-xl px-6 py-16 text-center">
        <h1 className="text-3xl font-bold text-slate-900">
          We couldn&rsquo;t confirm
        </h1>
        <p className="mt-4 text-slate-700">{message}</p>
        <Link
          href="/newsletter"
          className="mt-6 inline-block rounded-md bg-orange-600 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-700"
        >
          Subscribe again
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-xl px-6 py-16 text-center">
      <h1 className="text-3xl font-bold text-slate-900">You&rsquo;re in.</h1>
      <p className="mt-4 text-slate-700">
        Welcome to the Director's Brief. The first email lands in your inbox in about a
        minute. After that, expect Thursday morning emails.
      </p>
      <p className="mt-2 text-slate-700">
        If it doesn&rsquo;t show, check spam or promotions, and add{" "}
        <code className="rounded bg-slate-100 px-1 py-0.5 text-sm">
          hello@hollowaydavies.co.uk
        </code>{" "}
        to your contacts.
      </p>
      <Link
        href="/"
        className="mt-8 inline-block rounded-md bg-orange-600 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-700"
      >
        Back to the site
      </Link>
    </main>
  );
}
