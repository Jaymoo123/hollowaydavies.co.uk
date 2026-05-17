export function addHeadingIds(html: string): string {
  const headingRegex = /<(h[23])>(.*?)<\/\1>/gi;
  let counter = 0;
  const seen = new Set<string>();

  return html.replace(headingRegex, (match, tag, content) => {
    const text = content.replace(/<[^>]*>/g, "");
    const baseId = text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || `heading-${counter++}`;

    let uniqueId = baseId;
    let suffix = 2;
    while (seen.has(uniqueId)) {
      uniqueId = `${baseId}-${suffix++}`;
    }
    seen.add(uniqueId);

    return `<${tag} id="${uniqueId}">${content}</${tag}>`;
  });
}

export function extractHeadings(html: string): Array<{ id: string; text: string; level: number }> {
  const headingRegex = /<h([23])\s+id="([^"]+)">(.*?)<\/h\1>/gi;
  const headings: Array<{ id: string; text: string; level: number }> = [];
  let match;

  while ((match = headingRegex.exec(html)) !== null) {
    const level = parseInt(match[1]);
    const id = match[2];
    const text = match[3].replace(/<[^>]*>/g, "");
    headings.push({ id, text, level });
  }

  return headings;
}
