# Private adult demonstration (local only)

Prepared, not activated. Public EduTrack remains for its existing audience and has no external AI enabled. This separate demonstration is only for the owner and an adult professor, via screen sharing. Do not expose ports, create a public tunnel, deploy this launcher, or share the temporary login externally.

## No-key run

From `edutrack-api`:

```powershell
.\.venv\Scripts\python.exe scripts/run_adult_ai_demo.py --confirm-private-adults
```

The flag confirms private adult-only use. By default chat is disabled and the local planner works. SQLite contains only fictitious sample data and is deleted on normal shutdown. API listens only on `127.0.0.1:8014`. An ephemeral JWT is generated for each run. The launcher does not read `.env`, host environment settings, secret files, production database or Google data.

In a separate terminal, from `edutrack-app-completo`, using the existing production build:

```powershell
$env:EDUTRACK_API_URL='http://127.0.0.1:8014'
$env:EDUTRACK_SITE_URL='http://127.0.0.1:3014'
$env:HOSTNAME='127.0.0.1'
$env:PORT='3014'
node scripts/start-hostinger.mjs
```

These frontend variables affect only that terminal/process. Browse `http://127.0.0.1:3014/login`. Fictitious fixture login: `avaliacao@example.com`, password `Demonstracao-local-2026`. No professor account or real email is needed. Stop both processes after the demonstration. Do not reuse this fixture on a public service.

## Future live mode: authorization still required

Only after explicit approval of credential use and provider requests, add `--enable-live-gemini`. The launcher requires an interactive terminal and uses `getpass` to read the key privately; it does not save it to an environment variable, file, or log. It remains in process memory until shutdown, not guaranteed securely erased. Never provide the key as an argument, chat message or pipe.

`--model` accepts a configurable model ID; default candidate is `gemini-3.5-flash-lite`. Availability, free quota and the project's billing status must be confirmed separately before a live test. No availability or no-cost guarantee is made.

This instance alone uses `ai_audience=adults_only`, Gemini with academic context disabled, Classroom disabled, and no email delivery. Live mode rejects inherited proxy/certificate overrides rather than silently using them. Chat requires consent and adult declaration. Use generic, fictitious questions only. The local planner does not contact Gemini.

`gemini_paid_service=false` disables academic-context transmission. It DOES NOT disable Google billing or create a spending cap. Existing controls: 8 requests/minute per user, 20/minute per process, one Gemini request per general-chat turn, 1600 output-token cap, 30-second timeout. Restart resets in-memory rate limits. There is no daily or monetary hard cap. Cancellation stops waiting, not necessarily provider processing.

## Validation

Tests in `tests/test_adult_ai_demo.py` use SQLite and a mocked HTTP transport. They verify explicit activation guards, ignored inherited credentials, ephemeral JWT, no-key chat rejection, local planning, consent/adult checks, no academic context sent, official endpoint and output cap. These tests do not prove a real model is available or that the UI has been visually checked.
