import { redirect } from "next/navigation";

/**
 * The Digital Agency template included a 12-question health-check wizard
 * with sector-typed questions and a rules engine flavoured for marketing /
 * creative businesses. That intake form is the wrong shape for this generalist
 * site. For v1 we redirect to /contact; a re-engineered generalist intake
 * is on the Phase C roadmap.
 */
export default function FreeHealthCheckPage(): never {
  redirect("/contact");
}
