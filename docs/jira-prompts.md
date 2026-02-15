# Jira Ticket Writing Guide

## Quick Formula
Use this structure for useful Jira tickets:

`Why` + `What` + `How to know it's done`

## Jira Template

```md
Title:
[Feature/Bug/Task] Short, specific outcome

Context / Problem
- What is happening?
- Why it matters (user/business impact)

Scope
- In scope:
- Out of scope:

Requirements
- [ ] Requirement 1
- [ ] Requirement 2

Acceptance Criteria
- [ ] Given <context>, when <action>, then <result>
- [ ] Edge case handled: <case>
- [ ] No regression in <related area>

Technical Notes
- Systems/components affected:
- Dependencies:
- Risks:

Definition of Done
- [ ] Code complete
- [ ] Tests added/updated
- [ ] QA passed
- [ ] Docs updated (if needed)

Estimate
- Story points / effort:
```

## Example Jira Ticket

```md
Title:
[Bug] Checkout fails when promo code contains lowercase letters

Context / Problem
Users entering lowercase promo codes get "Invalid code" even when code is valid.
This causes failed checkouts and support tickets.

Scope
- In scope: promo code validation in checkout API
- Out of scope: admin promo creation UI

Requirements
- Normalize promo code input to uppercase before validation
- Preserve existing behavior for invalid/expired codes

Acceptance Criteria
- Given valid code "save10", when user applies it, then discount is applied
- Given invalid code, when applied, then user sees existing error message
- Given expired code, then expired-code message appears
- Existing uppercase code behavior remains unchanged

Technical Notes
- Affected: checkout-service, promo-validator
- Dependency: none
- Risk: discount logic regression

Definition of Done
- Unit tests for lowercase/uppercase/invalid/expired cases
- QA verifies in staging
- Release note added

Estimate
- 3 story points
```

## Reusable AI Prompt for Jira Creation

```md
Create a Jira ticket from this request: "<paste request>"

Output must include:
1) Title (clear and outcome-based)
2) Context/Problem (user + business impact)
3) Scope (in/out)
4) Requirements (checklist)
5) Acceptance Criteria (Given/When/Then, including edge cases)
6) Technical Notes (components, dependencies, risks)
7) Definition of Done
8) Suggested estimate (with rationale)

Constraints:
- Be specific and testable
- Avoid vague language
- Keep ticket under 250 words
```
