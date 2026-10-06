# Postmortem

## What went wrong
1. **We initially reused the previous unit-conversion bake-off.** That task had a single numeric answer and exact scoring, so it did not fit Project 1. We replaced it with customer-support reply evaluation, where multiple wordings can be good and a rubric is necessary.
2. **The first draft of the new dataset contained repeated inputs.** Repetition would make a 160-item count look larger without adding much evaluation coverage. We rebuilt the set as 160 unique policy/message pairs and added `dataset_check.py` to fail on duplicate inputs.
3. **Plain “return JSON” prompting was not enough.** Malformed JSON would make scoring depend on ad-hoc parsing. We switched both the system and judge to provider-enforced structured output backed by Pydantic schemas.
4. **Judge scores are not automatically trustworthy.** A judge can prefer the first answer or reward extra words. We added explicit A/B order swapping and verbosity-padding checks and report the failure rate rather than assuming neutrality.
5. **Long API runs can be interrupted or rate-limited.** The harness writes results after every item and supports `--resume`, so a partial run does not erase completed work.

## What we learned
Per-item evidence matters more than one headline score. Human agreement is necessary before treating the judge as a measurement tool, prompt changes must be tied to dev-set numbers, and held-out test data should not be used for tuning.

## What we would do differently
We would freeze the task and rubric earlier, pilot-label 10–15 examples before scaling to all 160, and reserve more time for the two independent labeling passes and for investigating concrete judge disagreements.
