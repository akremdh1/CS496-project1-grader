import json, os, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Defaults copied from the previous repo's pricing assumptions. Verify provider pricing on submission day.
DEFAULTS={
 'gemini-3.5-flash-lite': {'in':0.30,'out':2.50},
 'gemini-3.6-flash': {'in':1.50,'out':7.50},
}

def price(model):
    p=DEFAULTS.get(model)
    if p is None: return None
    return {'in':float(os.getenv('INPUT_USD_PER_MILLION',p['in'])), 'out':float(os.getenv('OUTPUT_USD_PER_MILLION',p['out']))}

def rows(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

for path in sorted((ROOT/'results').glob('*.jsonl')):
    if not (path.name.startswith('system_') or path.name.startswith('judged_')): continue
    rs=rows(path)
    model=(rs[0].get('model') or rs[0].get('judge_model')) if rs else None
    usable=[r for r in rs if r.get('input_tokens') is not None and r.get('output_tokens') is not None]
    if not usable or not model: continue
    p=price(model)
    if p is None:
        print(path.name,': add pricing for',model); continue
    ai=statistics.mean(float(r['input_tokens']) for r in usable); ao=statistics.mean(float(r['output_tokens']) for r in usable)
    per=(ai*p['in']+ao*p['out'])/1_000_000
    print(f'{path.name}: model={model}; n={len(usable)}; avg={ai:.1f} in/{ao:.1f} out; cost/item=${per:.6f}; cost/1k=${per*1000:.4f}; cost/100k=${per*100000:.2f}')
