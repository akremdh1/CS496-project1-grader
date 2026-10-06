import argparse, csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

ap = argparse.ArgumentParser()
ap.add_argument('--labeler', choices=['a', 'b'], required=True)
ap.add_argument('--version', default='v2', choices=['v1', 'v2'])
ap.add_argument('--split', default='all', choices=['dev', 'test', 'all'])
args = ap.parse_args()

src = ROOT / f'results/system_{args.version}_{args.split}.jsonl'
if not src.exists():
    raise SystemExit(f'Missing {src}. Run the system first.')
outputs = [json.loads(x) for x in src.read_text(encoding='utf-8').splitlines() if x.strip()]
path = ROOT / 'data/human_labels.csv'
rows = list(csv.DictReader(path.open(encoding='utf-8')))
byid = {int(r['item_id']): r for r in rows}
who = args.labeler
cols = [f'{who}_correctness', f'{who}_completeness', f'{who}_tone', f'{who}_non_fabrication']

def ask_dim(name):
    while True:
        s = input(f'{name} 0-2 (q=stop): ').strip().lower()
        if s == 'q':
            return None
        if s in {'0', '1', '2'}:
            return int(s)
        print('Enter 0, 1, or 2.')

for x in outputs:
    r = byid[int(x['id'])]
    if r.get('status', 'keep') == 'drop' or all(r[c].strip() for c in cols):
        continue
    print()
    print('=' * 90)
    print(f'ITEM {x["id"]} | {x["category"]} | {x["split"]}')
    print('POLICY:', x['policy'])
    print('CUSTOMER:', x['customer_message'])
    print('REFERENCE:', json.dumps(x['reference'], ensure_ascii=False))
    print('SYSTEM RESPONSE:', json.dumps(x.get('system_response'), ensure_ascii=False, indent=2))
    vals = []
    for name in ('correctness', 'completeness', 'tone', 'non_fabrication'):
        v = ask_dim(name)
        if v is None:
            break
        vals.append(v)
    if len(vals) < 4:
        break
    total = sum(vals)
    passed = total >= 6 and vals[0] >= 1 and vals[3] >= 1
    for c, v in zip(cols, vals):
        r[c] = str(v)
    r[f'{who}_total'] = str(total)
    r[f'{who}_pass'] = '1' if passed else '0'
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
print('Saved', path)
