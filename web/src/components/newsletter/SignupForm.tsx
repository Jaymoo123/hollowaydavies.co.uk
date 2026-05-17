"use client";

import { useState } from "react";

type Variant = "card" | "inline" | "minimal";

type Props = {
  variant?: Variant;
  source: string;
  heading?: string;
  body?: string;
  ctaLabel?: string;
  successMessage?: string;
  /** Retained for type compatibility with shared call sites; ignored. */
  showAgencyType?: boolean;
};

export function SignupForm({
  variant = "card",
  source,
  heading = "The Director's Brief",
  body = "A weekly note on UK business tax, structure, payroll and cash. Plain text, one CTA, unsubscribe one click.",
  ctaLabel = "Subscribe",
  successMessage = "Check your inbox to confirm your subscription.",
}: Props) {
  const [email, setEmail] = useState("");
  // Honeypot, humans never fill this; bots typically do. Filled => silent reject.
  const [website, setWebsite] = useState("");
  const [state, setState] = useState<"idle" | "submitting" | "ok" | "err">("idle");
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"confirm-required" | "collect-only" | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (state === "submitting") return;
    if (website) {
      setState("ok");
      return;
    }
    setState("submitting");
    setError(null);
    try {
      const res = await fetch("/api/newsletter/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          source,
          sourceUrl: typeof window !== "undefined" ? window.location.href : undefined,
        }),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j?.error || "Subscription failed");
      }
      const j = await res.json().catch(() => ({}));
      setMode(j?.mode === "collect-only" ? "collect-only" : "confirm-required");
      setState("ok");
      setEmail("");
    } catch (err) {
      setState("err");
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  const containerClass =
    variant === "card"
      ? "border border-neutral-200 bg-white p-8"
      : variant === "inline"
        ? "border-t border-b border-neutral-200 bg-transparent py-8"
        : "";

  if (state === "ok") {
    const headline = mode === "collect-only" ? "You’re on the list." : "Thanks. Almost done.";
    const body =
      mode === "collect-only"
        ? "We’ll email you as soon as the first edition goes out."
        : successMessage;
    return (
      <div className={containerClass} role="status" aria-live="polite">
        <p className="text-base font-medium text-neutral-900">{headline}</p>
        <p className="mt-2 text-sm text-neutral-600">{body}</p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className={containerClass} noValidate>
      <div aria-hidden="true" style={{ position: "absolute", left: "-9999px", width: 1, height: 1, overflow: "hidden" }}>
        <label htmlFor={`newsletter-website-${source}`}>Website (leave blank)</label>
        <input
          id={`newsletter-website-${source}`}
          type="text"
          tabIndex={-1}
          autoComplete="off"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
        />
      </div>
      {variant !== "minimal" && (
        <>
          <p className="font-mono text-xs uppercase tracking-widest text-orange-500">Newsletter</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-tight text-neutral-900">{heading}</h3>
          <p className="mt-2 text-sm leading-relaxed text-neutral-600 max-w-prose">{body}</p>
        </>
      )}
      <div className={variant === "minimal" ? "flex gap-2" : "mt-6 flex flex-col sm:flex-row gap-3"}>
        <label className="sr-only" htmlFor={`newsletter-email-${source}`}>
          Email address
        </label>
        <input
          id={`newsletter-email-${source}`}
          type="email"
          required
          autoComplete="email"
          inputMode="email"
          placeholder="you@yourbusiness.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="flex-1 min-w-0 border border-neutral-300 bg-white px-4 py-3 text-sm text-neutral-900 placeholder:text-neutral-400 transition-colors focus:outline-none focus:border-orange-500"
        />
        <button
          type="submit"
          disabled={state === "submitting"}
          className="inline-flex min-h-12 items-center justify-center bg-orange-500 px-6 py-3 text-sm font-medium text-white tracking-wide transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
        >
          {state === "submitting" ? "Subscribing..." : ctaLabel}
        </button>
      </div>
      {state === "err" && (
        <p className="mt-3 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {variant !== "minimal" && (
        <p className="mt-4 text-xs text-neutral-500">
          No spam. Unsubscribe one click. We never share your email.
        </p>
      )}
    </form>
  );
}
