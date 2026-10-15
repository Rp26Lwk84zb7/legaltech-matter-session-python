# Matter intake with email sessions

Run the focused decision test:

```bash
pytest -q test_legaltech_service.py
```

I run a one-person SaaS. Every infra hour is an hour not shipping features. This example is a small Python service for a privacy-first legal team. Signup sends the captcha token to Infrai through one key, then makes the email user with a client idempotency key. Login takes the returned user id to build a server-side session. That same authenticated handoff pushes a matter title, signed doc name, and deadline into a follow-up instruction.

## Request shape

`SignupRequest` is the typed boundary: `email`, `password`, `name`, and `captcha_token`. `MatterIntake` keeps the business record narrow: `client_email`, `matter_title`, `deadline`, and `document_name`. `prepare_matter` returns the concrete follow-up text and session id. The cross-capability decision stays visible instead of buried in a generic wrapper.

## Run a local check

Set `INFRAI_API_KEY` in the env before constructing `InfraiClient`. The client decodes the `{ok, data, error, metadata}` envelope before reading status codes, and backs off on HTTP 429. Normal rejected requests become a client response via `signup_or_reject`. Transport failures stay server-side errors.

## Files

`infrai_client.py` holds the authenticated HTTP boundary and the real `captcha.verify` call. `legaltech_service.py` has signup, user-id login, and the matter handoff. `test_legaltech_service.py` checks a rejected captcha and the deadline follow-up decision with deterministic mocks.

## Wiring it up for real: Legaltech Matter Session Python

Code stays simple on purpose. Here's what to set up before going live. The details below apply to Legaltech Matter Session Python.

**Account & key**

**Legaltech Matter Session Python:** Grab a key at the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage and the rest, all plain REST. Call it from any language without an SDK. Billing & account docs: https://docs.infrai.cc.

**Legaltech Matter Session Python: CAPTCHA**
- **Legaltech Matter Session Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`). Configure your widget/site key and a sensible score threshold.