import csv, json, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def jl(name):
    p = ROOT / name
    return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()] if p.exists() else []

def judge_summary(version, split):
    rows = [x for x in jl(f'results/judged_{version}_{split}.jsonl') if x.get('judgement')]
    if not rows:
        return None
    passed = sum(bool(r['judgement']['passed']) for r in rows)
    avg = statistics.mean(r['judgement']['overall_score'] for r in rows)
    return len(rows), passed, 100 * passed / len(rows), avg

print('SYSTEM / JUDGE SCORES')
for version, split in [('v1', 'dev'), ('v2', 'dev'), ('v2', 'test')]:
    s = judge_summary(version, split)
    if s:
        print(f'{version} {split}: pass {s[1]}/{s[0]} = {s[2]:.1f}% ; avg score {s[3]:.2f}/8')

labels_path = ROOT / 'data/human_labels.csv'
rows = list(csv.DictReader(labels_path.open(encoding='utf-8')))
kept = [r for r in rows if r.get('status', 'keep') != 'drop']
dropped = [r for r in rows if r.get('status', 'keep') == 'drop']
print()
print(f'DATASET: kept {len(kept)}/{len(rows)} ; dropped {len(dropped)}/{len(rows)} = {100 * len(dropped) / len(rows):.1f}%')
if dropped:
    reasons = {}
    for r in dropped:
        key = r.get('drop_reason') or 'unspecified'
        reasons[key] = reasons.get(key, 0) + 1
    print('Drop reasons:', reasons)

paired = [r for r in kept if r['a_total'].strip() and r['b_total'].strip()]
if paired:
    exact = sum(r['a_total'] == r['b_total'] for r in paired)
    within = sum(abs(int(r['a_total']) - int(r['b_total'])) <= 1 for r in paired)
    passagree = sum(r['a_pass'] == r['b_pass'] for r in paired)
    print()
    print(f'HUMAN AGREEMENT: exact {exact}/{len(paired)} = {100 * exact / len(paired):.1f}% ; within 1 {within}/{len(paired)} = {100 * within / len(paired):.1f}% ; pass/fail {passagree}/{len(paired)} = {100 * passagree / len(paired):.1f}%')
else:
    print()
    print('HUMAN AGREEMENT: no complete paired labels yet')

judged = {int(x['item_id']): x['judgement'] for x in jl('results/judged_v2_all.jsonl') if x.get('judgement')}
cons = [r for r in kept if r['consensus_total'].strip() and int(r['item_id']) in judged]
if cons:
    exact = sum(int(r['consensus_total']) == judged[int(r['item_id'])]['overall_score'] for r in cons)
    within = sum(abs(int(r['consensus_total']) - judged[int(r['item_id'])]['overall_score']) <= 1 for r in cons)
    passagree = sum((r['consensus_pass'] == '1') == bool(judged[int(r['item_id'])]['passed']) for r in cons)
    print(f'JUDGE vs CONSENSUS: exact {exact}/{len(cons)} = {100 * exact / len(cons):.1f}% ; within 1 {within}/{len(cons)} = {100 * within / len(cons):.1f}% ; pass/fail {passagree}/{len(cons)} = {100 * passagree / len(cons):.1f}%')
else:
    print('JUDGE vs CONSENSUS: consensus labels or judged_v2_all.jsonl missing')

bias = [x for x in jl('results/bias_checks.jsonl') if not x.get('error')]
if bias:
    pc = sum(bool(x['position_changed']) for x in bias)
    vi = sum(x['verbosity_delta'] > 0 for x in bias)
    print()
    print(f'POSITION BIAS: changed {pc}/{len(bias)} = {100 * pc / len(bias):.1f}%')
    print(f'VERBOSITY BIAS: grade increased {vi}/{len(bias)} = {100 * vi / len(bias):.1f}%')
