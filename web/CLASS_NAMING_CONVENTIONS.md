# Class Naming Convention

This document defines a single, consolidated convention for CSS/Tailwind class usage in the Property site.

## Scope

Use this convention for:
- `className` strings in React components
- shared class constants in `src/components/ui/layout-utils.ts`
- utility-style class composition in UI components

## 1) Naming Principles

- Be semantic first: name reusable constants by intent, not appearance.
- Keep classes predictable: follow a consistent ordering.
- Prefer existing design tokens and shared utilities before adding one-off classes.
- Avoid duplicate styling patterns; extract repeated class sets into constants.

## 2) Reusable Class Constant Names

When creating reusable class strings:
- Use `camelCase`.
- Prefix by role where helpful: `btn`, `card`, `section`, `text`, `focus`.
- Name for purpose, e.g. `btnPrimary`, `btnSecondary`, `focusRing`, `siteContainer`.
- Avoid color-specific names unless intentionally hard-coded for brand exceptions.

Examples:
- Good: `btnPrimary`, `sectionYLoose`, `contentNarrow`
- Avoid: `greenButton`, `bigPaddingBlock`

## 3) `className` Utility Ordering

Within a single `className` string, use this order:
1. Layout and position (`relative`, `flex`, `grid`, `sticky`, `top-0`)
2. Box model (`w-*`, `h-*`, `p-*`, `m-*`)
3. Typography (`text-*`, `font-*`, `leading-*`, `tracking-*`)
4. Visual (`bg-*`, `border-*`, `shadow-*`, `rounded-*`)
5. Effects and motion (`transition-*`, `duration-*`, `animate-*`)
6. State variants (`hover:*`, `focus:*`, `active:*`, `disabled:*`)
7. Responsive variants (`sm:*`, `md:*`, `lg:*`, `xl:*`)

Notes:
- Keep variant groups clustered near the base utility they modify when readability improves.
- For very long strings, prefer extraction into a named constant.

## 4) Variant and State Rules

- Always include accessible focus styles for interactive elements.
- Keep hover/active/focus variants aligned with the same color family unless intentionally contrasting.
- Use `disabled:*` styles on disabled-capable controls.

## 5) Color and Token Rules

- Prefer shared button and layout utilities from `layout-utils.ts`.
- For Property-specific brand styling, emerald is default unless product/UI decision says otherwise.
- If introducing a new recurring color pattern (e.g. blue CTA), extract a reusable class constant.

## 6) Examples

### Button Variant Constant

```ts
export const btnPrimaryBlue =
  "inline-flex min-h-12 min-w-[10rem] items-center justify-center bg-blue-600 px-8 py-3.5 text-base font-bold text-white border-b-4 border-blue-800 transition-all duration-150 hover:bg-blue-700 hover:border-blue-900 active:border-b-2 active:translate-y-0.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600";
```

### Component Usage

```tsx
<Link href="/contact" className={`${btnPrimary} sm:text-lg`}>
  Book free consultation
</Link>
```

## 7) Adoption Checklist

- Reuse existing constants first.
- If a class pattern repeats 2+ times, extract it.
- Keep class ordering consistent.
- Confirm visual changes in `npm run dev` before finalizing.
