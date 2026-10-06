import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT, load_jsonl, write_jsonl, read_text, get_client, call_structured, maybe_sleep
from schemas import JudgeResult, PairwiseResult

JUDGE_MODEL=os.getenv('JUDGE_MODEL','gemini-3.5-flash-lite')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--n',type=int,default=20); args=ap.parse_args()
    v1={int(x['id']):x for x in load_jsonl('results/system_v1_dev.jsonl') if x.get('system_response')}
    v2={int(x['id']):x for x in load_jsonl('results/system_v2_dev.jsonl') if x.get('system_response')}
    ids=sorted(set(v1)&set(v2))[:args.n]
    if not ids: raise SystemExit('Run v1 and v2 on the dev set first.')
    client=get_client(); out=[]
    judge_prompt=read_text('prompts/judge_v1.txt'); rubric=read_text('data/labelling_guide.md')
    padding=' Thank you for contacting us. We appreciate your patience and understanding. We hope this information is useful. Please let us know if there is anything else we can help with.'

    for k,i in enumerate(ids,1):
        a,b=v1[i],v2[i]
        base=f'''POLICY:
{a['policy']}
CUSTOMER MESSAGE:
{a['customer_message']}
REFERENCE CHECKLIST:
{json.dumps(a['reference'],ensure_ascii=False)}'''
        pair='''Compare response A and response B using the policy and reference checklist. Correctness and non-fabrication matter more than style. Do not prefer an answer because it appears first or is longer.'''
        try:
            p1=f'''{pair}
{base}
A:
{json.dumps(a['system_response'],ensure_ascii=False)}
B:
{json.dumps(b['system_response'],ensure_ascii=False)}'''
            p2=f'''{pair}
{base}
A:
{json.dumps(b['system_response'],ensure_ascii=False)}
B:
{json.dumps(a['system_response'],ensure_ascii=False)}'''
            j1,_=call_structured(client,JUDGE_MODEL,p1,PairwiseResult)
            j2,_=call_structured(client,JUDGE_MODEL,p2,PairwiseResult)
            identity1='v1' if j1.winner=='A' else 'v2' if j1.winner=='B' else 'tie'
            identity2='v2' if j2.winner=='A' else 'v1' if j2.winner=='B' else 'tie'

            def grade(response_obj):
                p=f'''{judge_prompt}
RUBRIC:
{rubric}
{base}
SYSTEM RESPONSE:
{json.dumps(response_obj,ensure_ascii=False)}'''
                g,_=call_structured(client,JUDGE_MODEL,p,JudgeResult); return g
            base_obj=dict(b['system_response'])
            padded_obj=dict(base_obj); padded_obj['reply']=base_obj['reply']+padding
            g0=grade(base_obj); gp=grade(padded_obj)
            out.append({'item_id':i,'winner_original_order':identity1,'winner_swapped_order':identity2,
                        'position_changed':identity1!=identity2,'base_score':g0.overall_score,
                        'padded_score':gp.overall_score,'verbosity_delta':gp.overall_score-g0.overall_score,'error':None})
        except Exception as e:
            out.append({'item_id':i,'error':str(e)})
        write_jsonl('results/bias_checks.jsonl',out)
        print(f'[{k}/{len(ids)}] item {i} done'); maybe_sleep()

    ok=[x for x in out if not x.get('error')]
    if ok:
        pc=sum(bool(x['position_changed']) for x in ok); vi=sum(x['verbosity_delta']>0 for x in ok)
        print(f'Position verdict changed: {pc}/{len(ok)} = {100*pc/len(ok):.1f}%')
        print(f'Padding increased grade: {vi}/{len(ok)} = {100*vi/len(ok):.1f}%')

if __name__=='__main__': main()
