import { Button, Section, Text } from "@react-email/components";
import * as React from "react";
import { EmailLayout } from "./EmailLayout";
import type { WelcomeStep } from "./content/welcome-series";

type Props = {
  step: WelcomeStep;
  unsubscribeUrl: string;
};

export default function WelcomeEmail({ step, unsubscribeUrl }: Props) {
  return (
    <EmailLayout preview={step.preview} unsubscribeUrl={unsubscribeUrl}>
      <Section>
        <Text style={greeting}>{step.greeting}</Text>
        {step.paragraphs.map((p, i) => (
          <Text key={i} style={paragraph}>
            {p}
          </Text>
        ))}
        <Button href={step.ctaUrl} style={button}>
          {step.ctaLabel}
        </Button>
        <Text style={sign}>{step.sign}</Text>
      </Section>
    </EmailLayout>
  );
}

const greeting: React.CSSProperties = {
  fontSize: "18px",
  fontWeight: 600,
  color: "#0f172a",
  margin: "0 0 16px",
};
const paragraph: React.CSSProperties = {
  fontSize: "15px",
  lineHeight: "24px",
  color: "#1e293b",
  margin: "0 0 14px",
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
  marginTop: "8px",
};
const sign: React.CSSProperties = {
  fontSize: "14px",
  color: "#475569",
  margin: "24px 0 0",
};
