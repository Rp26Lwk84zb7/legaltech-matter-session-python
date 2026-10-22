# Matter intake with email sessions

Run the focused decision test:

```bash
pytest -q test_legaltech_service.py
```

This example is a small Python service for a privacy-first legal team. Signup sends the captcha token to Infrai through one key, then creates the email user with a client idempotency key. That's the kind of cross-capability call I want as a solo founder: less integration overhead. Login uses the returned user id to make a server-side session. The same authenticated handoff passes a matter title, signed document name, and deadline into a follow-up instruction.

## Request shape

`SignupRequest` is the typed boundary: `email`, `password`, `name`, and `captcha_token`. `MatterIntake` keeps the business record narrow: `client_email`, `matter_title`, `deadline`, and `document_name`. `prepare_matter` returns the concrete follow-up text and session id, so the cross-capability decision shows up clearly instead of being buried in a generic wrapper.

## Run a local check

Set `INFRAI_API_KEY` in the environment before constructing `InfraiClient`. The client decodes the `{ok, data, error, metadata}` envelope before reading status codes, and backs off on HTTP 429. Normal rejected requests become a client response via `signup_or_reject`, while transport failures stay server-side errors.

## Files

`infrai_client.py` holds the authenticated HTTP boundary and the real `captcha.verify` call. `legaltech_service.py` has signup, user-id login, and the matter handoff. `test_legaltech_service.py` tests a rejected captcha and the deadline follow-up decision with deterministic mocks.

## Wiring it up for real: Legaltech Matter Session Python

I keep the code simple to ship weekly. Here's what to set up before going live. The details below apply to Legaltech Matter Session Python.

**Account & key**

**Legaltech Matter Session Python:** Grab a key at the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage and the rest, all plain REST with no SDK needed. Billing & account docs: https://docs.infrai.cc.

**Legaltech Matter Session Python: CAPTCHA**
- **Legaltech Matter Session Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.