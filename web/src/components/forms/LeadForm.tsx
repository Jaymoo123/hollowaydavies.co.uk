"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { btnPrimary } from "@/components/ui/layout-utils";
import { niche } from "@/config/niche-loader";
import { submitLead, getSupabaseConfig } from "@/lib/supabase-client";

const fieldClass =
  "mt-2 w-full min-h-12 touch-manipulation border border-neutral-300 bg-white px-3.5 py-3 text-base text-neutral-900 placeholder:text-neutral-400 transition-colors focus:border-orange-500 focus:outline-none";

const labelClass = "block text-sm font-medium text-neutral-900";
const errorClass = "mt-2 text-xs text-red-600";

type FormStatus = "idle" | "loading" | "success" | "error";

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const ukPhoneRe = /^[\d\s+().-]{10,}$/;

function hasMinDigits(phone: string, min: number): boolean {
  const digits = phone.replace(/\D/g, "");
  return digits.length >= min;
}

type LeadFormProps = {
  redirectOnSuccess?: boolean;
  submitLabel?: string;
  /** Destination on success when redirectOnSuccess is true. Defaults to /thank-you. */
  successRedirect?: string;
};

export function LeadForm({
  redirectOnSuccess = true,
  submitLabel = "Send enquiry",
  successRedirect = "/thank-you",
}: LeadFormProps) {
  const router = useRouter();
  const [status, setStatus] = useState<FormStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [sourceUrl, setSourceUrl] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      setSourceUrl(window.location.href);
    }
  }, []);

  const { supabaseUrl, supabaseKey } = getSupabaseConfig();

  const validate = useCallback((data: FormData) => {
    const errs: Record<string, string> = {};
    const fullName = String(data.get("fullName") || "").trim();
    const email = String(data.get("email") || "").trim();
    const phone = String(data.get("phone") || "").trim();
    const role = String(data.get("role") || "").trim();
    const message = String(data.get("message") || "").trim();

    if (fullName.length < 2) errs.fullName = "Enter your name.";
    if (!emailRe.test(email)) errs.email = "Enter a valid email address.";

    if (!ukPhoneRe.test(phone)) {
      errs.phone = "Use only digits, spaces, +, -, ( ) for example 07700 900123";
    } else if (!hasMinDigits(phone, 10)) {
      errs.phone = "Enter at least 10 digits.";
    }

    if (!role) errs.role = "Select an option.";

    if (message.length > 0 && message.length < 10) {
      errs.message = "Add a sentence or two if you have a specific question.";
    }

    return errs;
  }, []);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErrorMessage(null);
    const form = e.currentTarget;
    const data = new FormData(form);
    const errs = validate(data);
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) return;

    if (!supabaseUrl || !supabaseKey) {
      setStatus("error");
      setErrorMessage(
        "Form not connected. Email us directly and we will respond same day.",
      );
      return;
    }

    setStatus("loading");
    const payload = {
      full_name: String(data.get("fullName") || "").trim(),
      email: String(data.get("email") || "").trim(),
      phone: String(data.get("phone") || "").trim(),
      role: String(data.get("role") || "").trim(),
      practice_name: "",
      message: String(data.get("message") || "").trim(),
      source: niche.content_strategy.source_identifier,
      source_url: sourceUrl || String(data.get("sourceUrl") || "").trim(),
      submitted_at: new Date().toISOString(),
    };

    const result = await submitLead(payload, supabaseUrl, supabaseKey);

    if (!result.success) {
      setStatus("error");
      setErrorMessage(result.error || "Something went wrong. Please try again or email us directly.");
      return;
    }

    if (typeof window !== "undefined" && "gtag" in window) {
      const gtag = (window as { gtag?: (...args: unknown[]) => void }).gtag;
      if (gtag) {
        gtag("event", "generate_lead", {
          event_category: "engagement",
          event_label: `${niche.niche_id}_${payload.role}`,
          value: 1,
        });
      }
    }

    setStatus("success");
    form.reset();

    if (redirectOnSuccess) {
      setTimeout(() => {
        router.push(successRedirect);
      }, 800);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6" noValidate aria-busy={status === "loading"}>
      <input type="hidden" name="sourceUrl" value={sourceUrl} />

      <div>
        <label htmlFor="role" className={labelClass}>
          {niche.lead_form.role_label}
        </label>
        <select
          id="role"
          name="role"
          required
          autoComplete="off"
          className={fieldClass}
          aria-invalid={!!fieldErrors.role}
          aria-describedby={fieldErrors.role ? "role-error" : undefined}
        >
          <option value="">Select...</option>
          {niche.lead_form.role_options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {fieldErrors.role && (
          <p id="role-error" className={errorClass}>
            {fieldErrors.role}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="fullName" className={labelClass}>
          Full name
        </label>
        <input
          type="text"
          id="fullName"
          name="fullName"
          required
          autoComplete="name"
          maxLength={100}
          placeholder={niche.lead_form.placeholders.name}
          className={fieldClass}
          aria-invalid={!!fieldErrors.fullName}
          aria-describedby={fieldErrors.fullName ? "fullName-error" : undefined}
        />
        {fieldErrors.fullName && (
          <p id="fullName-error" className={errorClass}>
            {fieldErrors.fullName}
          </p>
        )}
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="email" className={labelClass}>
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            required
            autoComplete="email"
            maxLength={100}
            placeholder={niche.lead_form.placeholders.email}
            className={fieldClass}
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? "email-error" : undefined}
          />
          {fieldErrors.email && (
            <p id="email-error" className={errorClass}>
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="phone" className={labelClass}>
            Phone
          </label>
          <input
            type="tel"
            id="phone"
            name="phone"
            required
            autoComplete="tel"
            maxLength={20}
            placeholder={niche.lead_form.placeholders.phone}
            className={fieldClass}
            aria-invalid={!!fieldErrors.phone}
            aria-describedby={fieldErrors.phone ? "phone-error" : undefined}
          />
          {fieldErrors.phone && (
            <p id="phone-error" className={errorClass}>
              {fieldErrors.phone}
            </p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="message" className={labelClass}>
          Message <span className="font-normal text-neutral-500">(optional)</span>
        </label>
        <textarea
          id="message"
          name="message"
          rows={4}
          maxLength={1000}
          placeholder={niche.lead_form.placeholders.message}
          className={fieldClass}
          aria-invalid={!!fieldErrors.message}
          aria-describedby={fieldErrors.message ? "message-error" : undefined}
        />
        {fieldErrors.message && (
          <p id="message-error" className={errorClass}>
            {fieldErrors.message}
          </p>
        )}
      </div>

      {errorMessage && (
        <div role="alert" className="border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      {status === "success" && !redirectOnSuccess && (
        <div role="status" className="border border-orange-200 bg-orange-50 p-4">
          <p className="text-sm font-medium text-orange-900">
            Thanks. We&apos;ll be in touch within 24 hours.
          </p>
        </div>
      )}

      <button
        type="submit"
        disabled={status === "loading" || status === "success"}
        className={`${btnPrimary} w-full`}
      >
        {status === "loading" ? "Sending..." : status === "success" ? "Sent" : submitLabel}
      </button>

      <p className="text-xs leading-relaxed text-neutral-500">
        We respond within 24 hours. Your details are stored securely and never shared.
      </p>
    </form>
  );
}
