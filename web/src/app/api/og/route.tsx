import { ImageResponse } from "next/og";
import type { NextRequest } from "next/server";

export const runtime = "edge";

const BRAND_COLOR = "#4f46e5";
const BRAND_NAME = "Holloway Davies";

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl;
  const title = searchParams.get("title") ?? "Holloway Davies";
  const category = searchParams.get("category") ?? "";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "white",
          padding: "60px",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >
          {category && (
            <span
              style={{
                fontSize: 24,
                fontWeight: 600,
                color: BRAND_COLOR,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              {category}
            </span>
          )}
          <h1
            style={{
              fontSize: title.length > 60 ? 40 : 52,
              fontWeight: 700,
              color: "#1e293b",
              lineHeight: 1.2,
              margin: 0,
            }}
          >
            {title}
          </h1>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: BRAND_COLOR,
            }}
          >
            {BRAND_NAME}
          </span>
          <span
            style={{
              fontSize: 20,
              color: "#64748b",
            }}
          >
            hollowaydavies.co.uk
          </span>
        </div>
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "8px",
            background: BRAND_COLOR,
          }}
        />
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
