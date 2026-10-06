import subprocess, sys
from pathlib import Path

def run(*args):
    cmd = [sys.executable, *args]
    print()
    print('>>>', ' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True)

# Prompt development uses DEV only. TEST is run only for the final v2 prompt.
run('harness/dataset_check.py')
run('harness/runner.py', '--version', 'v1', '--split', 'dev', '--resume')
run('harness/judge.py', '--version', 'v1', '--split', 'dev', '--resume')
run('harness/runner.py', '--version', 'v2', '--split', 'dev', '--resume')
run('harness/judge.py', '--version', 'v2', '--split', 'dev', '--resume')
run('harness/runner.py', '--version', 'v2', '--split', 'test', '--resume')
run('harness/judge.py', '--version', 'v2', '--split', 'test', '--resume')
run('harness/bias_checks.py', '--n', '20')

# Build all-output files for labeling/reliability without re-calling the model.
root = Path(__file__).resolve().parent
(root / 'results/system_v2_all.jsonl').write_text(
    (root / 'results/system_v2_dev.jsonl').read_text(encoding='utf-8') +
    (root / 'results/system_v2_test.jsonl').read_text(encoding='utf-8'),
    encoding='utf-8'
)
(root / 'results/judged_v2_all.jsonl').write_text(
    (root / 'results/judged_v2_dev.jsonl').read_text(encoding='utf-8') +
    (root / 'results/judged_v2_test.jsonl').read_text(encoding='utf-8'),
    encoding='utf-8'
)
run('harness/metrics.py')
run('harness/cost_report.py')
print()
print('API evaluation finished. Next: two independent human labelers run harness/label.py, then consensus.py, metrics.py, and update report.md.')
