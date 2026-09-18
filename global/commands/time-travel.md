---
description: Time-travel a plan or decision — visit a future where it failed and work backward to figure out why.
---

# /time-travel

Time-travel a plan, launch, decision, hire, partnership, or pivot. The frame matters: visit a future where it has already failed, then work backward to explain why. That shifts analysis from agreeable risk-assessment into honest failure identification.

Don't run on vague ideas, factual questions, draft-editing requests, or already-irreversible decisions.

## 1. Context

Skim the conversation and workspace. Confirm you can state in one sentence each:

a. **What it is** — the specific plan or decision.
b. **Who it affects** — audience, customer, team, stakeholders.
c. **Success criterion** — the outcome being aimed at.

If one is missing, ask one tight question. Don't interrogate.

## 2. Frame

Tell the human explicitly:

> "It's 6 months from now. [The plan] has failed. We're working backward to understand why."

The explicit "it has failed" frame is the mechanism that makes the rest work. Skip it and you get polite risk-assessment instead of honest failure identification.

## 3. Raw failure list

Generate every genuine reason it could have died. Specific to this plan, grounded in real details, not generic advice. Stop when the list is real — could be 3, could be 9. Don't pad. Don't clip. One or two sentences per reason.

## 4. Parallel deep-dives

Spawn one Task agent per failure reason, all in a single message so they run in parallel. Subagent type: `general-purpose`. Each agent gets:

a. The plan (what / who / success), plus relevant workspace context.
b. Its assigned failure reason.
c. The 6-months-out frame.
d. Output, capped at 300 words:
   1. **Failure story** — 2–3 paragraph narrative of how this specific failure played out, with named moments and real details.
   2. **Underlying assumption** — the one thing taken for granted that made this failure possible. One sentence.
   3. **Early warning signs** — 1–2 observable signals the human could watch for to detect this failure mode starting.

## 5. Synthesis

Read every deep-dive and produce in the chat:

a. **Most likely failure** — most probable scenario given what's known. Address first.
b. **Most dangerous failure** — most damaging if it hit, even if less likely. Insure against.
c. **Hidden assumption** — the single biggest thing taken for granted across all analyses. Often the real value of the trip.
d. **Revised plan** — concrete changes mapped to specific failure modes. State actions the human can do this week, not "consider your pricing."
e. **Pre-launch checklist** — 3–5 specific verifications, tests, or guardrails. Each prevents or detects a specific failure mode.

## 6. Save

Save the full transcript (context, raw list, deep-dives, synthesis) as markdown to `docs/scratch/time-travel-<slug>.md` (slug: 2–4 word kebab-case from what was time-traveled). The chat synthesis is the product; the file is the record. No HTML report.
