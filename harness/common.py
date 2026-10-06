import json, os, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]

def load_jsonl(rel):
    p = ROOT / rel
    if not p.exists(): return []
    return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]

def write_jsonl(rel, rows):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')

def read_text(rel):
    return (ROOT / rel).read_text(encoding='utf-8').strip()

def get_client():
    from google import genai
    key = os.getenv('GOOGLE_API_KEY')
    if not key:
        raise RuntimeError('GOOGLE_API_KEY is missing. Create a .env file in the repo root.')
    return genai.Client(api_key=key)

def _usage(response):
    u = getattr(response, 'usage_metadata', None)
    if u is None:
        return None, None
    inp = getattr(u, 'prompt_token_count', None)
    out = getattr(u, 'candidates_token_count', None)
    return inp, out

def call_structured(client, model, prompt, schema, temperature=0):
    import random

    max_attempts = 8
    base_delay = float(os.getenv('REQUEST_DELAY_SECONDS', '5'))

    for attempt in range(1, max_attempts + 1):
        try:
            # Space out every API call to stay under the free-tier rate limit.
            time.sleep(base_delay)

            start = time.perf_counter()

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    'temperature': temperature,
                    'response_mime_type': 'application/json',
                    'response_schema': schema,
                },
            )

            latency_ms = (time.perf_counter() - start) * 1000

            parsed = getattr(response, 'parsed', None)

            if parsed is None:
                parsed = schema.model_validate_json(response.text)
            elif not isinstance(parsed, schema):
                parsed = schema.model_validate(parsed)

            inp, out = _usage(response)

            return parsed, {
                'latency_ms': round(latency_ms, 1),
                'input_tokens': inp,
                'output_tokens': out
            }

        except Exception as e:
            msg = str(e)

            retryable = (
                '429' in msg
                or 'RESOURCE_EXHAUSTED' in msg
                or 'getaddrinfo failed' in msg
                or 'temporarily unavailable' in msg.lower()
                or 'timeout' in msg.lower()
                or 'connection' in msg.lower()
            )

            if not retryable or attempt == max_attempts:
                raise

            delay = max(base_delay, min(60, 5 * attempt)) + random.uniform(0, 2)

            print(
                f'API transient error '
                f'(attempt {attempt}/{max_attempts}); '
                f'retrying after {delay:.1f}s: {msg[:120]}'
            )

            time.sleep(delay)

def maybe_sleep():
    time.sleep(float(os.getenv('REQUEST_DELAY_SECONDS','0')))
