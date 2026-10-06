# Project 1 — The Grader — Report

## 1. Task and why exact match is not enough

This project evaluates customer-support replies generated from a short policy and a customer message. There is no single correct wording for many support questions: different responses may communicate the same valid decision in different ways. Therefore, exact string matching would incorrectly reject many good responses.

We instead evaluate each reply using four dimensions:

- **Correctness** — whether the answer follows the supplied policy.
- **Completeness** — whether all important required points are addressed.
- **Tone** — whether the response is professional, clear, and concise.
- **Non-fabrication** — whether the response avoids unsupported facts, promises, procedures, or outcomes.

The system returns a structured customer-facing reply, an action field, and an `escalation_needed` flag.

## 2. Golden set and labelling

The golden set contains **160 unique items** across 10 customer-support categories. The dataset is divided into:

- **120 development items**
- **40 held-out test items**

Each item contains a policy, customer message, and a reference checklist containing required points, forbidden claims, the expected decision, and the expected escalation behavior.

The final dataset validation produced:

- **Items kept:** 160/160 = **100.0%**
- **Items dropped:** 0/160 = **0.0%**
- **Unique inputs:** 160/160

Human-label agreement was:

- **Exact four-score agreement:** 153/160 = **95.6%**
- **Agreement within one point:** 160/160 = **100.0%**
- **Pass/fail agreement:** 160/160 = **100.0%**

## 3. Harness

`runner.py` performs one system-model call per item and stores one JSONL result row containing the input, structured system output, latency, token usage, prompt version, and any error.

The model output is constrained using the provider's structured-output mechanism and the `SupportResponse` schema instead of relying on free-text JSON parsing.

`judge.py` evaluates each system response using the same four-dimensional rubric. Judge output is also constrained to a structured `JudgeResult`.

The dataset checker confirmed:

- 160 total items
- 120 development items
- 40 test items
- 16 items in each of the 10 support categories
- 160 unique inputs
- Dataset check: **PASS**

## 4. Judge reliability and bias

Judge agreement with consensus was:

- **Exact score agreement:** 135/160 = **84.4%**
- **Agreement within one point:** 151/160 = **94.4%**
- **Pass/fail agreement:** 159/160 = **99.4%**

Known judge/evaluation disagreements included:

- **Item 42:** an unsupported carrier-investigation condition affected the non-fabrication score.
- **Item 45:** the response stated a stronger restriction than the policy supported.
- **Item 61:** the response added an unsupported claim that cancellation would not erase the customer's account.

Position-bias test:

- **Verdict changed:** 4/14 = **28.6%**

Verbosity-bias test:

- **Grade increased after padding:** 0/14 = **0.0%**

## 5. System and prompt history

v1 was the baseline prompt.

Development-set performance:

- **117/120 passed = 97.5%**
- **Average score = 7.57/8**

v2 strengthened the prompt by targeting omissions, unsupported promises, review-vs-guarantee mistakes, next-step quality, and consistency of structured fields.

Development-set performance improved to:

- **120/120 passed = 100.0%**
- **Average score = 7.93/8**

Held-out test performance:

- **39/40 passed = 97.5%**
- **Average score = 7.85/8**

## 6. Cost and latency

For the final **v2 system model**:

- **$0.000308 per system request**
- **$0.3075 per 1,000 requests**
- **$30.75 per 100,000 requests**

For the **v2 judge**:

- **$0.000535 per judged item**
- **$0.5351 per 1,000 judged items**
- **$53.51 per 100,000 judged items**

Latency for the 160 final v2 system requests:

- **n = 160**
- **Mean = 1268.26 ms ≈ 1.27 s**
- **p50 = 1199.7 ms ≈ 1.20 s**
- **p95 = 1673.1 ms ≈ 1.67 s**
- **Minimum = 959.8 ms**
- **Maximum = 2168 ms ≈ 2.17 s**

## 7. Final results

| Measure | Result |
|---|---:|
| v1 dev pass rate | 117/120 = 97.5% |
| v1 dev average | 7.57/8 |
| v2 dev pass rate | 120/120 = 100.0% |
| v2 dev average | 7.93/8 |
| v2 held-out test pass rate | 39/40 = 97.5% |
| v2 held-out test average | 7.85/8 |
| Human exact agreement | 153/160 = 95.6% |
| Human within-one agreement | 160/160 = 100.0% |
| Human pass/fail agreement | 160/160 = 100.0% |
| Judge/consensus exact agreement | 135/160 = 84.4% |
| Judge/consensus within-one agreement | 151/160 = 94.4% |
| Judge/consensus pass/fail agreement | 159/160 = 99.4% |
| Position-bias verdict changes | 4/14 = 28.6% |
| Verbosity-bias grade increases | 0/14 = 0.0% |

Overall, v2 improved over the baseline on the development set and maintained a **97.5% pass rate on the held-out test set**.
