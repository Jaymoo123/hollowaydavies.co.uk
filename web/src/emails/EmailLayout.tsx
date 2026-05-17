import {
  Body,
  Container,
  Head,
  Hr,
  Html,
  Link,
  Preview,
  Section,
  Text,
} from "@react-email/components";
import * as React from "react";

const BRAND = "#4f46e5";

type Props = {
  preview: string;
  children: React.ReactNode;
  unsubscribeUrl?: string;
};

/**
 * Plain-text-feel email layout. Single column, generous whitespace,
 * minimal HTML chrome. Designed to land in inbox not promotions tab.
 */
export function EmailLayout({ preview, children, unsubscribeUrl }: Props) {
  return (
    <Html lang="en">
      <Head />
      <Preview>{preview}</Preview>
      <Body style={body}>
        <Container style={container}>
          <Section style={header}>
            <Text style={brand}>Holloway Davies</Text>
          </Section>
          {children}
          <Hr style={hr} />
          <Section style={footer}>
            <Text style={footerText}>
              Holloway Davies Ltd · ICAEW qualified · Specialist
              accountants for UK limited companies, contractors, sole traders
              and partnerships.
            </Text>
            <Text style={footerText}>
              <Link href="https://www.hollowaydavies.co.uk" style={footerLink}>
                hollowaydavies.co.uk
              </Link>
              {unsubscribeUrl ? (
                <>
                  {"  ·  "}
                  <Link href={unsubscribeUrl} style={footerLink}>
                    Unsubscribe
                  </Link>
                </>
              ) : null}
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const body: React.CSSProperties = {
  backgroundColor: "#f8fafc",
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  color: "#0f172a",
  margin: 0,
  padding: 0,
};

const container: React.CSSProperties = {
  backgroundColor: "#ffffff",
  margin: "0 auto",
  padding: "32px 24px 24px",
  maxWidth: "560px",
};

const header: React.CSSProperties = {
  paddingBottom: "16px",
};

const brand: React.CSSProperties = {
  color: BRAND,
  fontWeight: 700,
  fontSize: "14px",
  margin: 0,
  letterSpacing: "0.5px",
  textTransform: "uppercase",
};

const hr: React.CSSProperties = {
  borderColor: "#e2e8f0",
  margin: "32px 0 16px",
};

const footer: React.CSSProperties = {
  paddingTop: "0",
};

const footerText: React.CSSProperties = {
  color: "#64748b",
  fontSize: "12px",
  lineHeight: "18px",
  margin: "4px 0",
};

const footerLink: React.CSSProperties = {
  color: "#475569",
  textDecoration: "underline",
};
