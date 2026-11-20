# Closed adult access: prepared, not deployed

Owner-approved scope: online access only for explicitly named adults, no charges, no personal or Classroom data sent to Gemini. No accounts are deleted and existing academic data is preserved. Listing an email is an operator attestation of the owner's adult-access decision, NOT automatic age verification. Email verification proves mailbox possession, not age.

## Configuration, OFF by default

- `EDUTRACK_CLOSED_ADULT_ACCESS=false` by default.
- `EDUTRACK_ADULT_ACCESS_EMAILS=[]` by default, JSON array of explicitly approved adult emails. Never publish this list.
- Activation would require `EDUTRACK_CLOSED_ADULT_ACCESS=true` and `EDUTRACK_AI_AUDIENCE=adults_only`.
- With closed mode on, empty list or incompatible audience denies everyone. Every login and authenticated API request checks the allowlist AND database email confirmation. Old JWTs cannot bypass removal from the list. Google OAuth start/callback require the same current-user guard before external calls.
- ALL self-registration is disabled, including listed addresses. Approved accounts must already exist before access. An allowlisted unverified account can request/confirm its own email with valid credentials, but cannot enter the app until verified; its login returns EMAIL_VERIFICATION_REQUIRED. The existing email-verification feature and sender must be enabled for this flow. Excluded accounts cannot request/confirm email in closed mode. New professor account provisioning requires a separate authorized workflow; no automatic account creation is included.
- `/api/auth/options` exposes only `restricted_adults_mode`, `registration_enabled` and ordinary existing options, never addresses. Frontend should display the closed adult audience and suppress signup.
- Public login, health, privacy and explanatory pages remain available; academic data, integration operations, admin and AI require authorized accounts. This is application-level access control, not a reverse-proxy password wall.
- Email verification/password recovery never grant an exception to the allowlist; next login/current-user check still requires it. Existing records are not removed or altered by mode activation.

## Gemini and zero-charge requirement

No key or live configuration was read or changed for this preparation. Production Gemini additionally requires closed mode and a nonempty approved list before reporting configured. Closed mode forces Gemini academic context OFF even if the old paid-service flag was set. The general chat does not call tools and uses the official Gemini endpoint, one request per question, 1600 output tokens and 30-second timeout. Classroom content is not automatically sent; do not type private/personal data into prompts.

`EDUTRACK_GEMINI_PAID_SERVICE=false` is NOT a billing lock. Before any activation, verify the actual Google project has no enabled billing and the exact selected model has a usable free quota in that project/region. If billing is enabled or zero charge cannot be established, STOP. Do not enable billing, buy credits, use paid tools, switch models, or add a fallback provider. Model unavailability/quota exhaustion must remain an error with the local planner available. No paid or alternate-model fallback exists in the current adapter.

A named model is not proof of free availability. User approved zero spending. Key storage/use still follows the specific approved destination; never put credentials in repository, command arguments or logs.

## Activation decisions pending

1. Confirm the existing owner account and adult operator(s). Latest owner instruction: the professor will not log in; the group will record a video using the owner account. Do not create a professor account or request the professor email; do not share passwords.
2. Confirm each account exists and has email confirmation, without modifying academic data.
3. Verify free-only project/model conditions; otherwise do not activate Gemini.
4. Approve deployment and the restrictive access change with its effect on excluded existing users; preserve rollback and all data.
5. Validate closed mode anonymously, with excluded old sessions, and with approved account before any authorized synthetic test prompt.

Tests: SQLite and mock providers only. They cover default behavior, private options, denied registration, rejected old sessions across APIs, unverified/removed accounts, OAuth/chat denial before clients, production configuration gating and forced exclusion of academic context. No live Gemini test has been run.


## Executed state: 16 November 2026

Closed access was published in release `edutrack-closed-20261116-230807`, after explicit approval of the owner's existing academic account and adult operator. Exactly one verified account is allowed; signup is disabled. API/web health checks passed; five pages and fifteen assets returned 200; anonymous private APIs returned 401 and signup returned 403. Direct server-side guard validation permitted the approved owner and denied the other existing account, without manufacturing a login or token. Live browser login was not performed.

Gemini remains disabled with no Gemini/OpenAI key present; no model request, billing activation or payment occurred. The private key handoff and verification of free-only project/model conditions remain pending.

At the owner's request, the account's local academic data was cleared for recording after a native SQL backup with checksum/VERIFYONLY and a private typed snapshot. A SERIALIZABLE transaction rehearsed clear, restore and exact snapshot/protected-row equality, then rolled back. The final clear committed only after this rehearsal succeeded. Courses, disciplines, tasks, Classroom local contents/links and study sessions are zero; weekly reports were already zero. Account, email verification, credentials, Google connection and all other users' data remained unchanged by fingerprints. Classroom was not modified; imports are explicit, not automatic.

Safe operational evidence is under `output/edutrack-closed-20261116` and `output/edutrack-cleanup-20261116` in the project. Academic snapshot contents stay only in the private server backup directory, not in public documentation or delivery bundles. See the publication record in the delivery documentation for restoration boundaries.
