# Troubleshooting — sdk_agents (Streamlit deployment)

Runbook for when the deployed app (or local Streamlit run) stops producing
answers. Written after a real multi-hour incident — see git log on
`sdk_agents/core/base_agent.py` for the full blow-by-blow commit history.

**Current known-good config:** `LLM_PROVIDER=gemini`, `GEMINI_MODEL` defaults
to `gemini-3.1-flash-lite` in `core/base_agent.py`. This will drift over time
— see [Known issues](#known-issues) below.

---

## Fast diagnosis

1. **Read the actual error, not the friendly UI message.** The Streamlit UI
   always shows a generic message to the user (`renderer.py`). The real
   exception is logged:
   - **Locally:** `sdk_agents/logs/renderer.log` and `sdk_agents/logs/<agent-name>.log`
   - **On Streamlit Cloud:** open the app → bottom-right **"Manage app"** →
     scroll the log panel for the red traceback. This is the single most
     useful diagnostic step — do this before changing any code.

2. **Reproduce locally against the same live keys** rather than guessing:
   ```bash
   python -c "
   from dotenv import load_dotenv
   load_dotenv('sdk_agents/.env')
   from sdk_agents.integrator.can_bus_analyst import CanBusAnalystAgent
   agent = CanBusAnalystAgent()
   print('provider:', agent.provider, '| model:', agent.gemini_model)
   result = agent.run('CAN node goes bus-off after 3 minutes, only when engine running')
   print(type(result).__name__)
   if type(result).__name__ == 'AgentError':
       print(result.error_type, result.message)
   "
   ```
   `can-bus-analyst` is a good default probe — it has one of the largest
   prompts, so it surfaces token-budget problems fastest.

3. **Check whether it's local-only or also broken on the deployed app.**
   Local working + Cloud broken almost always means one of:
   - Streamlit Cloud **Secrets** don't match your local `.env` (see below)
   - `requirements.txt` isn't pinned, so Cloud resolved a different package
     version than what you tested locally

---

## Known issues

### "Something went wrong — please try again" (generic message)
This is the fallback in `renderer.py` for anything not specifically
classified. Check `renderer.log` / Cloud logs for the real exception —
it's always logged there before the friendly message is shown.

### `404 ... does not exist or you do not have access to it` (model retired)
The pinned model name (`GROQ_MODEL` / `GEMINI_MODEL` in `base_agent.py`) has
been deprecated by the provider. List what's actually available on your key:
```python
# Groq
client.models.list()
# Gemini
for m in client.models.list(): print(m.name)
```
Pick a replacement, update the default in `base_agent.py`, verify live
end-to-end (see step 2 above) before pushing.

### `413 ... Request too large ... tokens per minute (TPM)` (Groq only)
Groq's free tier only supports strict `json_schema` structured output on
**two models** (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`), both capped at
**8,000 TPM**. Several of this project's agent prompts (`sw-integrator`,
`sw-unit-tester`, `gate-review-approver`, etc.) exceed that on their own,
independent of retries or `max_tokens`. This is not fixable by picking a
different Groq model — it's a hard ceiling. Use `LLM_PROVIDER=gemini`
instead, which has much more headroom.

### `429` / rate limited, message says "retry in Ns"
Short-term, per-minute limit — not a daily cap. `base_agent.py` fails fast
on these (`error_type: "rate_limited"`) instead of retrying immediately,
specifically because immediate retries make rate limiting worse. Just wait
the stated time and try once.

### Gemini quota exhausted almost immediately (e.g. `limit: 20`)
Check which **model** the quota error names — it's per-model. If it's an
alias like `gemini-flash-latest` / `gemini-pro-latest`, that alias tracks
whichever model is *newest*, and brand-new models ship with far stingier
free-tier quotas than established ones. **Never default to a `-latest`
alias for this reason.** Pin to a named, established version instead (check
`client.models.list()` for what's currently available) and verify its quota
empirically by running a handful of real calls — don't deliberately burn
quota probing for the exact number, that recreates the same problem.

### Gemini calls taking 90+ seconds, or intermittent `503 UNAVAILABLE`
This is Google's backend reporting "high demand" for that specific model —
an external, transient condition, not a code bug. The `-lite` variant of
whatever flash model you're on is usually less congested and meaningfully
faster (verified: `gemini-3.5-flash` was hitting 90-140s stalls under load;
`gemini-3.1-flash-lite` handled the same prompts in 4-14s with no quality
loss visible in the structured output). Try switching to it as a first move
before assuming something is actually broken.

### Works locally, still broken on Streamlit Cloud
Streamlit Cloud reads secrets from its own dashboard, **never** from your
local `.env` (which is git-ignored on purpose — check with
`git check-ignore -v sdk_agents/.env` before ever considering committing it).
Go to **share.streamlit.io → your app → Settings → Secrets** and confirm
these three keys are actually saved there (not just typed locally):
```
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "..."
GROQ_API_KEY = "..."
```
Saving triggers an automatic restart.

### Public link redirects to `share.streamlit.io/-/auth/app` (login wall)
Separate setting from Secrets. The app's viewer access is set to private.
**Settings → General** (wording varies by Streamlit version) → find the
"who can view this app" control → set to public. A private app and a
crashed app look identical to an outside visitor (or to an unauthenticated
fetch) — both just show the login wall — so fix this setting *and* verify
in an incognito window before concluding the app itself is broken.

### Deployed dependency version differs from what you tested locally
`requirements.txt` entries without a pinned version (e.g. `google-genai>=1.0`)
let Streamlit Cloud's resolver install something you never tested — this
actually happened (Cloud had resolved `google-genai==2.16.0` against a local
dev/test of `1.68.0`). Pin exact versions for anything whose API shape you
depend on directly, not just a floor with `>=`.

### One agent intermittently fails a *domain* check (not a provider error)
If `error_type` is `validation_error` or `domain_check_failed` (not
`rate_limited` / `api_error`), that's the semantic validator layer catching
a genuinely incomplete or wrong answer — e.g. a model skipping a required
calculation. This is model-quality flakiness, more common on lighter/faster
models (`flash-lite`-class) under detailed multi-step instructions. It's
usually not worth chasing as a "bug" — retry once. If it fails consistently
(not just occasionally) on one specific agent, that agent's prompt may need
stronger reinforcement of that specific requirement.

---

## Diagnostic commands reference

```bash
# Full local test suite (fast, mocked, no API key needed)
python -m pytest sdk_agents/tests/ -q

# Confirm which provider/model an agent will actually use
python -c "
from dotenv import load_dotenv
load_dotenv('sdk_agents/.env')
from sdk_agents.developer.misra_reviewer import MisraReviewerAgent
a = MisraReviewerAgent()
print(a.provider, a.groq_model, a.gemini_model)
"

# Sweep all 13 agents live against whatever LLM_PROVIDER is currently set
# (see docs/architecture.md section 6/7 for the full agent list/import paths)

# Check Groq's real-time rate-limit headroom for a model
python -c "
from dotenv import load_dotenv; load_dotenv('sdk_agents/.env')
import os
from groq import Groq
c = Groq(api_key=os.getenv('GROQ_API_KEY'))
r = c.chat.completions.with_raw_response.create(model='openai/gpt-oss-120b', messages=[{'role':'user','content':'hi'}], max_tokens=5)
print(r.headers.get('x-ratelimit-remaining-requests'), '/', r.headers.get('x-ratelimit-limit-requests'))
"

# List models actually available on a key (both providers)
python -c "
from dotenv import load_dotenv; load_dotenv('sdk_agents/.env')
import os
from groq import Groq
for m in Groq(api_key=os.getenv('GROQ_API_KEY')).models.list().data: print(m.id)
"
python -c "
from dotenv import load_dotenv; load_dotenv('sdk_agents/.env')
import os
from google import genai
for m in genai.Client(api_key=os.getenv('GEMINI_API_KEY')).models.list(): print(m.name)
"
```

---

## If you paste secrets into a chat/terminal by accident

It happened once already during this project's setup. Rotate the exposed
credential once things are stable — don't leave it live indefinitely just
because nothing bad happened yet:
- Groq key → regenerate at console.groq.com
- Gemini key → regenerate at aistudio.google.com/apikey
- `ANALYTICS_SECRET` (gates the `?admin=true` dashboard) → pick a new value
- Supabase key → regenerate in Supabase project settings
