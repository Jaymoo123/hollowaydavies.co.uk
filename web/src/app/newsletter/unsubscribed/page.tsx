import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Unsubscribed | Holloway Davies",
  robots: { index: false, follow: false },
};

export default function UnsubscribedPage() {
  return (
    <main className="mx-auto max-w-xl px-6 py-16 text-center">
      <h1 className="text-3xl font-bold text-slate-900">You&rsquo;re out.</h1>
      <p className="mt-4 text-slate-700">
        You won&rsquo;t hear from the Director's Brief again. If this was a mistake or
        you change your mind, you can{" "}
        <Link href="/newsletter" className="text-orange-600 underline">
          re-subscribe
        </Link>
        .
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
