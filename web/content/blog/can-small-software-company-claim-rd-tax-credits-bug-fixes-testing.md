---
title: "Can a Small Software Company Claim R&D Tax Credits for Time Spent on Bug Fixes and Testing?"
slug: "can-small-software-company-claim-rd-tax-credits-bug-fixes-testing"
canonical: "https://www.hollowaydavies.co.uk/blog/randd-tax-credits/can-small-software-company-claim-rd-tax-credits-bug-fixes-testing"
date: "2026-05-17"
author: "Holloway Davies Editorial Team"
category: "R&D Tax Credits"
metaTitle: "R&D tax credits bug fixes testing: software company"
metaDescription: "Can bug fixes and testing qualify for R&D tax credits? Yes, in specific circumstances. We explain the HMRC boundary for software development claims."
altText: "Software developer working on code at a desk in a modern UK office with dual monitors and notebooks"
image: "/blog/can-small-software-company-claim-rd-tax-credits-bug-fixes-testing.jpg"
imageCredit:
  photographer: "Naboth Otieno"
  photographerUrl: "https://www.pexels.com/@naboth-otieno-83498565"
  sourceUrl: "https://www.pexels.com/photo/man-working-on-computer-in-an-office-19805876/"
  source: "Pexels"
h1: "Can a Small Software Company Claim R&D Tax Credits for Time Spent on Bug Fixes and Testing?"
summary: "Bug fixes and testing can qualify for R&D tax credits, but only if they resolve genuine technological uncertainties. Routine debugging or regression testing does not count. We explain where HMRC draws the line for software companies."
schema: ""
faqs:
  - question: "Can I claim R&D tax credits for fixing bugs in an existing product?"
    answer: "Only if the bug arises from a technological uncertainty that was unresolved at the time the product was developed. Routine maintenance bug fixes do not qualify. If you are fixing bugs that appeared during the original R&D project and the solution required experimentation, those hours can be included in your claim."
  - question: "Does automated testing count as R&D expenditure?"
    answer: "Automated testing is R&D only if it is conducted to resolve a technological uncertainty, not to confirm known behaviour. Writing automated tests to verify standard functionality is routine quality assurance and does not qualify. Writing tests to explore how a novel algorithm behaves under unknown conditions can qualify."
  - question: "How do I prove that my bug fixes involved technological uncertainty?"
    answer: "Document the problem before you start fixing it. Record what you tried, what did not work, and why. Note the resources you consulted and why they did not provide a solution. If a competent developer could have fixed the bug using standard documentation or common knowledge, it is not R&D. Your records should demonstrate that the fix required genuine experimentation."
  - question: "What happens if HMRC challenges my R&D claim for bug fixes and testing?"
    answer: "HMRC may open a compliance check and request supporting evidence. If your claim includes routine bug fixes and testing without proper documentation, they may reduce or reject the claim. Penalties can apply if the claim is found to be deliberately overstated. Working with an ICAEW-qualified accountant who specialises in R&D claims significantly reduces this risk."
---

<p>If you run a small software company in the UK, you have probably heard that R&D tax credits can be valuable. The question is whether the time your developers spend fixing bugs and running tests counts as qualifying R&D expenditure.</p>

<p>The short answer is: yes, sometimes. But the boundary is narrower than many directors assume. HMRC does not treat all bug fixes and testing as R&D. The work must resolve a <strong>technological uncertainty</strong> that a competent professional in the field could not resolve through routine methods.</p>

<p>In this post we explain exactly where that boundary sits, using real scenarios a small software company might face. We also cover how to document the work so your <a href="/r-and-d-credits">R&D tax credits</a> claim survives HMRC scrutiny.</p>

<h2>What HMRC Means by Technological Uncertainty</h2>

<p>R&D tax credits exist to reward companies that advance science or technology by resolving uncertainty. For software, that means you are trying to do something that is not routine or readily deducible by a competent professional in your field.</p>

<p>HMRC defines technological uncertainty as work where the outcome is not known in advance and cannot be determined by standard practice. If you are following a well-known pattern or fixing a known bug type using documented methods, that is not R&D.</p>

<p>But if you are trying to solve a problem where no established solution exists, and you have to experiment, test hypotheses, and iterate to find an answer, that work can qualify. The testing and bug fixing that forms part of that iterative process can then be included.</p>

<h2>When Bug Fixes Qualify as R&D</h2>

<p>Bug fixes qualify for R&D tax credits when they form part of a wider R&D project. The key test is whether the bug arises from a technological uncertainty that the project is trying to resolve.</p>

<p>Consider a Manchester-based software company building a new image recognition algorithm for medical diagnostics. The team encounters unexpected behaviour when processing low-light images. No published research or standard library handles this specific combination of noise and colour depth. The team runs experiments, tests different approaches, and eventually fixes the bug through novel work.</p>

<p>That bug fix is R&D. It resolved a genuine technological uncertainty. The time spent testing different solutions and verifying the fix also qualifies.</p>

<p>Now consider a Bristol ecommerce company that finds a checkout page crashes when a user enters a postcode with a space. The developer knows the fix: trim whitespace before validation. They write the fix in ten minutes and test it. That is routine debugging. It does not qualify.</p>

<h3>Common R&D-Qualifying Bug Fix Scenarios</h3>

<p>Based on claims we have prepared for software clients at <a href="/about">Holloway Davies</a>, these patterns tend to qualify:</p>

<ul>
<li>Fixing performance bottlenecks in novel algorithms where standard optimisation techniques fail</li>
<li>Resolving data corruption issues in custom file formats that no existing tool handles</li>
<li>Debugging race conditions in multi-threaded systems where the timing is unpredictable and requires novel synchronisation approaches</li>
<li>Fixing integration bugs between new hardware and custom software where the hardware behaviour is not fully documented</li>
</ul>

<p>In each case, the fix required experimentation and learning. The developer did not know the answer at the start.</p>

<h2>When Testing Qualifies as R&D</h2>

<p>Testing follows the same principle. Routine regression testing, unit testing, and user acceptance testing do not qualify. They are standard practice and involve no technological uncertainty.</p>

<p>But testing that is part of an R&D project can qualify if it is conducted to resolve a technological uncertainty. For example, a team building a new compiler might run thousands of test cases to understand how the compiler handles edge cases in a novel optimisation pass. The testing is not routine. It is part of the experimentation needed to determine whether the approach works.</p>

<p>HMRC's guidelines use the phrase "testing of hypotheses". If you are testing to learn something unknown about the technology, it counts. If you are testing to confirm that something already known works correctly, it does not.</p>

<h3>Examples of Qualifying vs Non-Qualifying Testing</h3>

<p><strong>Qualifying:</strong> A software consultancy in Shoreditch builds a prototype for a real-time video compression algorithm. The team runs tests at different bitrates and resolutions to understand how the algorithm performs. The results are unpredictable. The testing reveals unexpected artefacts that require further development. The time spent on this testing is R&D.</p>

<p><strong>Non-qualifying:</strong> The same consultancy runs a standard suite of unit tests after every code commit to check that existing features still work. No uncertainty exists. The tests either pass or fail based on known criteria. That is routine quality assurance.</p>

<h2>The Boundary: What HMRC Looks For</h2>

<p>HMRC's R&D specialists review claims for software development with particular scrutiny. They look for evidence that the work went beyond routine software engineering. The following factors help demonstrate that bug fixes and testing are R&D:</p>

<ul>
<li><strong>Documented uncertainty.</strong> You should record what was unknown at the start of each work period. What specific technical problem were you trying to solve?</li>
<li><strong>Experimentation.</strong> Show that you tried multiple approaches, discarded some, and iterated. A single fix with no alternatives considered is unlikely to qualify.</li>
<li><strong>Competent professional test.</strong> Could a reasonably skilled developer have solved the problem using standard methods? If yes, it is not R&D.</li>
<li><strong>Records of time.</strong> Your developers should log time against specific R&D projects, not generic "bug fixing" or "testing" categories.</li>
</ul>

<p>Our <a href="/glossary">glossary of R&D terms</a> covers the key definitions HMRC uses when assessing claims.</p>

<h2>How to Structure Your Claim for Bug Fixes and Testing</h2>

<p>If you are claiming R&D tax credits for software development, you need to separate qualifying work from routine work. Do not lump all bug fixes and testing into the claim. HMRC will challenge it.</p>

<p>Instead, identify specific R&D projects. For each project, document:</p>

<ul>
<li>The technological uncertainty you faced at the start</li>
<li>The work you did to resolve it, including experiments and testing</li>
<li>The bugs you encountered that arose from the uncertainty, not from coding errors</li>
<li>The testing you conducted to validate your solution</li>
</ul>

<p>Then allocate the relevant staff time to the project. Use timesheets or project management tools to track hours. HMRC accepts reasonable estimates if precise records are not available, but the more detail you have, the stronger your claim.</p>

<p>As <a href="/services">ICAEW-qualified accountants</a>, we help software companies prepare R&D claims that meet HMRC's technical and financial requirements. The key is to tell the story of the technological advance, not just list hours spent.</p>

<h2>Common Mistakes Small Software Companies Make</h2>

<p>We see the same errors repeatedly when reviewing R&D claims for software businesses in Leeds, Glasgow, and Birmingham. Avoid these:</p>

<p><strong>Claiming all development time.</strong> HMRC expects you to separate routine development from R&D. If you claim everything, you invite a full review.</p>

<p><strong>Using vague descriptions.</strong> "Bug fixing" and "testing" are not enough. Describe the technical problem and why it was uncertain.</p>

<p><strong>Including post-release support.</strong> Bug fixes made after the product is released are usually maintenance, not R&D. Only pre-release work on unresolved uncertainties qualifies.</p>

<p><strong>Ignoring the competent professional test.</strong> If you would expect a graduate developer to fix the bug within a day using Stack Overflow, it is not R&D.</p>

<h2>Real Numbers: What a Claim Might Look Like</h2>

<p>A small software company in Birmingham's Jewellery Quarter employs four developers. One senior developer spends 40% of their time over six months on an R&D project building a new natural language processing library. During that project, they encounter bugs in the tokenisation logic that require novel solutions. They also run extensive tests to validate the library against edge cases. The qualifying time is 40% of that senior developer's salary plus employer NI and pension contributions.</p>

<p>If the senior developer earns £63,400 per year, the qualifying cost is £25,360 (40% of salary) plus employer NI at 13.8% and pension at 3%. Total qualifying cost: approximately £29,600. At the 19% small profits rate of corporation tax, that reduces the company's tax bill by roughly £5,620. If the company is loss-making, it can surrender the loss for a cash credit worth up to 14.5% of the qualifying cost.</p>

<p>That is a meaningful saving for a small business. But only if the claim is properly structured and documented.</p>

<h2>What About the Merged R&D Scheme?</h2>

<p>From 1 April 2024, the UK merged the old SME and RDEC schemes into a single scheme for most companies. The new rules apply to accounting periods starting on or after 1 April 2024. Under the merged scheme, the payable credit rate is lower for loss-making companies, but the principles for what qualifies as R&D have not changed.</p>

<p>If your company is R&D intensive (spending 30% or more of total costs on R&D) and loss-making, you may qualify for the enhanced R&D Intensive Scheme (ERIS), which provides a higher payable credit. Bug fixes and testing that meet the qualifying criteria count toward that 30% threshold.</p>

<p>Speak to your accountant about which scheme applies to your company's circumstances. The rules are complex, and getting it wrong can mean overclaiming or missing out.</p>

<h2>Final Thoughts on Bug Fixes, Testing, and R&D Credits</h2>

<p>R&D tax credits for software development are not a blanket entitlement. They reward genuine technological advances. Bug fixes and testing can qualify, but only when they resolve uncertainties that a competent professional could not solve through routine methods.</p>

<p>The best approach is to identify your R&D projects early, document the uncertainties, and track time carefully. If you are unsure whether your work qualifies, <a href="/contact">contact our team</a>. We review software R&D claims regularly and can tell you within a short conversation whether your bug fixes and testing are likely to qualify.</p>

<p>Do not assume that all development work is R&D. But do not assume that bug fixes and testing can never qualify either. The truth is somewhere in between, and it depends entirely on the nature of the technical problem you are solving.</p>
