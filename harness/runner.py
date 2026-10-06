import argparse, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_jsonl, write_jsonl, read_text, get_client, call_structured, maybe_sleep
from schemas import SupportResponse

SYSTEM_MODEL = os.getenv('SYSTEM_MODEL','gemini-3.5-flash-lite')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--version',choices=['v1','v2'],default='v2')
    ap.add_argument('--split',choices=['dev','test','all'],default='all')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()

    items=load_jsonl('data/golden_set.jsonl')
    if args.split!='all': items=[x for x in items if x['split']==args.split]
    if args.limit: items=items[:args.limit]
    prompt=read_text(f'prompts/system_{args.version}.txt')
    out_rel=f'results/system_{args.version}_{args.split}.jsonl'
    existing=load_jsonl(out_rel) if args.resume else []
    by_id={int(x['id']):x for x in existing}
    client=get_client()

    for n,item in enumerate(items,1):
        if item['id'] in by_id:
            print(f'[{n}/{len(items)}] item {item["id"]} SKIP (resume)')
            continue
        full=f'''{prompt}

POLICY:
{item['policy']}

CUSTOMER MESSAGE:
{item['customer_message']}'''
        try:
            parsed,meta=call_structured(client,SYSTEM_MODEL,full,SupportResponse)
            row={**item,'prompt_version':args.version,'model':SYSTEM_MODEL,
                 'system_response':parsed.model_dump(),**meta,'error':None}
        except Exception as e:
            row={**item,'prompt_version':args.version,'model':SYSTEM_MODEL,
                 'system_response':None,'latency_ms':None,'input_tokens':None,'output_tokens':None,'error':str(e)}
        by_id[item['id']]=row
        ordered=[by_id[i['id']] for i in items if i['id'] in by_id]
        write_jsonl(out_rel,ordered)  # save after every item
        print(f'[{n}/{len(items)}] item {item["id"]} {"OK" if not row["error"] else "ERROR"}')
        maybe_sleep()
    print('Wrote',ROOT/out_rel)

if __name__=='__main__': main()
