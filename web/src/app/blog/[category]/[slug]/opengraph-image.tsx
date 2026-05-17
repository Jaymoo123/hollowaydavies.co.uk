import { ImageResponse } from "next/og";
import { getPostByCategoryAndSlug } from "@/lib/blog";

export const runtime = "nodejs";
export const alt = "Blog post image";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({
  params,
}: {
  params: Promise<{ category: string; slug: string }>;
}) {
  const { category, slug } = await params;
  const post = getPostByCategoryAndSlug(category, slug);

  const title = post?.h1 || post?.title || "Holloway Davies";
  const categoryName = post?.category || "Blog";

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "#0f172a",
          padding: "60px",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "24px",
            }}
          >
            <div
              style={{
                backgroundColor: "#4f46e5",
                color: "#fff",
                padding: "6px 16px",
                borderRadius: "4px",
                fontSize: "18px",
                fontWeight: 700,
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}
            >
              {categoryName}
            </div>
          </div>
          <div
            style={{
              color: "#fff",
              fontSize: title.length > 60 ? 42 : 52,
              fontWeight: 700,
              lineHeight: 1.2,
              maxWidth: "900px",
            }}
          >
            {title}
          </div>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
          }}
        >
          <div
            style={{
              color: "#94a3b8",
              fontSize: 22,
              fontWeight: 600,
            }}
          >
            hollowaydavies.co.uk
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                backgroundColor: "#4f46e5",
                borderRadius: "8px",
              }}
            />
            <div style={{ color: "#e2e8f0", fontSize: 20, fontWeight: 600 }}>
              Holloway Davies
            </div>
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
