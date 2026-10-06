import json, collections
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/golden_set.jsonl'
rows=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
print('items:',len(rows))
print('split:',dict(collections.Counter(r['split'] for r in rows)))
print('categories:',dict(collections.Counter(r['category'] for r in rows)))
print('unique inputs:',len(set((r['policy'],r['customer_message']) for r in rows)))
assert len(rows)>=150
assert len(set(r['id'] for r in rows))==len(rows)
assert len(set((r['policy'],r['customer_message']) for r in rows))==len(rows)
assert set(r['split'] for r in rows)=={'dev','test'}
print('dataset check: PASS')
