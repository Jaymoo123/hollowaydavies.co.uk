import { SignupForm } from "./SignupForm";

type Props = {
  source: string;
  heading?: string;
  body?: string;
};

/**
 * Drop into the middle or end of a blog post. Renders an indigo-tinted card
 * with the newsletter signup. Contextual copy can be passed per category.
 */
export function InlinePrompt({
  source,
  heading = "Get the Director's Brief in your inbox.",
  body = "One short email a week. UK tax for limited companies, contractors, sole traders and small businesses. Plain text, unsubscribe one click.",
}: Props) {
  return (
    <aside className="my-10 not-prose">
      <SignupForm
        variant="inline"
        source={source}
        heading={heading}
        body={body}
        ctaLabel="Subscribe"
      />
    </aside>
  );
}
