# Project 1 — The Grader
CS496 AI Engineering

## Task
Generate customer-support replies from a short policy and evaluate their quality. There is no single correct wording: a good answer must be policy-correct, complete, professional, and non-fabricated.

## Setup — one command
```bash
python -m pip install -r requirements.txt
```
Create a `.env` file in the repository root (never commit it):
```text
GOOGLE_API_KEY=YOUR_KEY_HERE
SYSTEM_MODEL=gemini-3.5-flash-lite
JUDGE_MODEL=gemini-3.5-flash-lite
REQUEST_DELAY_SECONDS=1
```

## Run — one command
```bash
python run_all.py
```
The script is resumable and saves after every item. Prompt development uses only the dev split; the held-out test split is used only for final v2 reporting.

## Human labels (required by the brief)
After `run_all.py`, **two team members independently label all 160 final v2 replies**:
```bash
python harness/label.py --labeler a --version v2 --split all
python harness/label.py --labeler b --version v2 --split all
python harness/consensus.py
python harness/metrics.py
```
Do not fabricate human agreement. Keep the original A/B labels even after consensus.

## Bias checks
`run_all.py` tests both required judge biases on 20 dev items:
- **Position bias:** compare v1/v2 as A/B, then swap order.
- **Verbosity bias:** add irrelevant polite padding without adding useful content and re-grade.

## Repository structure
- `data/golden_set.jsonl` — 160 unique items, 120 dev + 40 held-out test
- `data/labelling_guide.md` — written 0–8 rubric with examples
- `data/human_labels.csv` — independent labels + consensus + drop reasons
- `harness/runner.py` — one system call/item; provider-enforced structured output
- `harness/judge.py` — LLM judge; provider-enforced structured output
- `harness/metrics.py` — system scores, human agreement, judge reliability, bias counts/percentages
- `harness/bias_checks.py` — position and verbosity checks
- `prompts/` — versioned prompts and changelog
- `results/` — per-item results from every run
- `report.md` — four-page report source; insert measured numbers only
- `postmortem.md` — failures and lessons

## Results
Run `python harness/metrics.py` after experiments and human labeling. Copy the printed **counts and percentages** into `report.md` and `prompts/CHANGELOG.md`. Do not report only one summary number.

## Contributions
- Akrem Dhib
- Hamza Lakoud
- Youssef Bouattour
- Mohamed Amine Zribi

## Clean-clone check
Before submission, clone the repo into a new folder and verify:
```bash
python -m pip install -r requirements.txt
python harness/dataset_check.py
```
Then set `.env` and run a small smoke test if quota permits:
```bash
python harness/runner.py --version v2 --split dev --limit 2
```
