import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_jsonl, write_jsonl, read_text, get_client, call_structured, maybe_sleep
from schemas import JudgeResult

JUDGE_MODEL=os.getenv('JUDGE_MODEL','gemini-3.5-flash-lite')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--version',choices=['v1','v2'],default='v2')
    ap.add_argument('--split',choices=['dev','test','all'],default='all')
    ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()
    src=f'results/system_{args.version}_{args.split}.jsonl'
    rows=load_jsonl(src)
    if not rows: raise SystemExit(f'Missing/empty {ROOT/src}; run runner.py first.')
    judge_prompt=read_text('prompts/judge_v1.txt')
    out_rel=f'results/judged_{args.version}_{args.split}.jsonl'
    existing=load_jsonl(out_rel) if args.resume else []
    by_id={int(x['item_id']):x for x in existing}
    client=get_client()
    rubric=read_text('data/labelling_guide.md')

    for n,row in enumerate(rows,1):
        iid=int(row['id'])
        if iid in by_id:
            print(f'[{n}/{len(rows)}] item {iid} SKIP (resume)'); continue
        if row.get('system_response') is None:
            result={'item_id':iid,'split':row['split'],'prompt_version':args.version,'judge_model':JUDGE_MODEL,
                    'judgement':None,'latency_ms':None,'input_tokens':None,'output_tokens':None,
                    'error':'system response missing'}
        else:
            p=f'''{judge_prompt}

RUBRIC:
{rubric}

POLICY:
{row['policy']}

CUSTOMER MESSAGE:
{row['customer_message']}

REFERENCE CHECKLIST:
{json.dumps(row['reference'],ensure_ascii=False)}

SYSTEM RESPONSE:
{json.dumps(row['system_response'],ensure_ascii=False)}'''
            try:
                parsed,meta=call_structured(client,JUDGE_MODEL,p,JudgeResult)
                result={'item_id':iid,'split':row['split'],'prompt_version':args.version,'judge_model':JUDGE_MODEL,
                        'judgement':parsed.model_dump(),**meta,'error':None}
            except Exception as e:
                result={'item_id':iid,'split':row['split'],'prompt_version':args.version,'judge_model':JUDGE_MODEL,
                        'judgement':None,'latency_ms':None,'input_tokens':None,'output_tokens':None,'error':str(e)}
        by_id[iid]=result
        ordered=[by_id[int(r['id'])] for r in rows if int(r['id']) in by_id]
        write_jsonl(out_rel,ordered)
        print(f'[{n}/{len(rows)}] item {iid} {"OK" if not result["error"] else "ERROR"}')
        maybe_sleep()
    print('Wrote',ROOT/out_rel)

if __name__=='__main__': main()
