# Labelling guide — Customer-support reply quality

## What you label
Read the **POLICY**, **CUSTOMER MESSAGE**, the item reference checklist, and the **SYSTEM RESPONSE**. Score the response independently. Do not discuss a score with the other labeler until both labels are saved.

The reference checklist is not an exact answer. It identifies required policy points and claims that must not be invented. Many different replies can still be fully correct.

## Four dimensions (0–2 each)

### 1. Correctness
- **2** — Fully consistent with the policy and gives the correct decision/action.
- **1** — Minor imprecision that does not materially change what the customer should do.
- **0** — Contradicts the policy, authorizes an unavailable exception, or gives materially wrong instructions.

### 2. Completeness
- **2** — Addresses every important concern and includes the important next step/condition.
- **1** — Main question is answered, but a secondary required point is missing.
- **0** — Main request is not answered or the required next step is omitted.

### 3. Tone and clarity
- **2** — Professional, respectful, concise, and easy to follow.
- **1** — Understandable but awkward, cold, repetitive, or unnecessarily verbose.
- **0** — Rude, confusing, dismissive, or inappropriate.

### 4. Non-fabrication
- **2** — No unsupported facts, links, dates, statuses, fees, promises, or exceptions.
- **1** — Small unsupported detail that does not materially affect the customer.
- **0** — Material invented fact or promise, e.g. saying a refund was issued when the policy only allows review.

## Total and pass/fail
`total = correctness + completeness + tone + non_fabrication` (0–8).

A response **passes** only when:
- total >= 6,
- correctness >= 1, and
- non-fabrication >= 1.

## Structured fields
The system also returns `action` and `escalation_needed`. If these fields contradict the written reply or policy, reduce **Correctness**. Do not give extra credit merely for matching wording.

## Examples
**Good:** Policy says a damaged item reported within 7 days with a photo may be reviewed for replacement or refund. The reply asks for the photo and says the team can review the case, without promising an outcome.

**Bad:** Same case, but the reply says “Your replacement is approved and ships tomorrow.” This invents an approval and date, so correctness and non-fabrication should be 0.

## Dropping an item
Drop an item only if the input itself is broken or ambiguous enough that two careful humans cannot apply this guide. Record the reason in `data/human_labels.csv`. Do not drop an item just because the model answered badly.

## Disagreements
After both independent labels are complete, run `python harness/consensus.py`. Discuss only disagreements and enter the final consensus dimensions. Preserve the original A/B labels for the agreement report.
