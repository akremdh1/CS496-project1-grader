import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data/human_labels.csv'
rows = list(csv.DictReader(path.open(encoding='utf-8')))
dims = ('correctness', 'completeness', 'tone', 'non_fabrication')

for r in rows:
    if r.get('status', 'keep') == 'drop':
        continue
    if not all(r[f'{who}_{d}'].strip() for who in ('a', 'b') for d in dims):
        continue
    a = [int(r[f'a_{d}']) for d in dims]
    b = [int(r[f'b_{d}']) for d in dims]
    if a == b:
        c = a
    else:
        print()
        print('Item', r['item_id'], 'A=', a, 'B=', b)
        c = []
        for d, av, bv in zip(dims, a, b):
            if av == bv:
                c.append(av)
                continue
            while True:
                s = input(f'Consensus {d} (A={av}, B={bv}) 0-2: ').strip()
                if s in {'0', '1', '2'}:
                    c.append(int(s))
                    break
    total = sum(c)
    passed = total >= 6 and c[0] >= 1 and c[3] >= 1
    for d, v in zip(dims, c):
        r[f'consensus_{d}'] = str(v)
    r['consensus_total'] = str(total)
    r['consensus_pass'] = '1' if passed else '0'

with path.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print('Saved consensus labels to', path)
