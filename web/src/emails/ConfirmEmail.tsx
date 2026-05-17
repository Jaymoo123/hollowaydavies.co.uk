import { Button, Link, Section, Text } from "@react-email/components";
import * as React from "react";
import { EmailLayout } from "./EmailLayout";

type Props = {
  confirmUrl: string;
};

export default function ConfirmEmail({ confirmUrl }: Props) {
  return (
    <EmailLayout preview="Confirm your subscription to The Director's Brief">
      <Section>
        <Text style={h1}>Confirm your subscription</Text>
        <Text style={p}>
          Thanks for signing up to <strong>The Director's Brief</strong>, a
          weekly read for UK business owners on tax, pay, structure, and exit.
        </Text>
        <Text style={p}>One last step. Confirm your email:</Text>
        <Button href={confirmUrl} style={button}>
          Confirm subscription
        </Button>
        <Text style={pSmall}>
          Or paste this link into your browser:
          <br />
          <Link href={confirmUrl} style={link}>
            {confirmUrl}
          </Link>
        </Text>
        <Text style={pMuted}>
          If you didn&rsquo;t sign up, you can ignore this email. No further
          messages will be sent.
        </Text>
      </Section>
    </EmailLayout>
  );
}

const h1: React.CSSProperties = {
  fontSize: "22px",
  fontWeight: 700,
  color: "#0f172a",
  marginBottom: "16px",
};
const p: React.CSSProperties = {
  fontSize: "15px",
  lineHeight: "24px",
  color: "#1e293b",
  margin: "0 0 16px",
};
const pSmall: React.CSSProperties = {
  fontSize: "13px",
  lineHeight: "20px",
  color: "#475569",
  margin: "16px 0",
  wordBreak: "break-all",
};
const pMuted: React.CSSProperties = {
  fontSize: "13px",
  lineHeight: "20px",
  color: "#64748b",
  margin: "24px 0 0",
};
const button: React.CSSProperties = {
  backgroundColor: "#4f46e5",
  color: "#ffffff",
  padding: "12px 24px",
  borderRadius: "6px",
  fontWeight: 600,
  textDecoration: "none",
  display: "inline-block",
  fontSize: "15px",
};
const link: React.CSSProperties = {
  color: "#4f46e5",
};
