# TODO - Task 1: Permanent Admin Login (Production Ready)

## Plan Summary
- Remove random/dev admin password generation from startup bootstrap.
- Add production env vars: DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD.
- Make AdminService.bootstrap_defaults idempotent: if admin exists, do nothing.
- If admin missing, create admin with hashed DEFAULT_ADMIN_PASSWORD.
- Preserve existing password reset feature and auth architecture.

## Steps
- [ ] Update app/core/config.py to add DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD settings.
- [ ] Update app/services/admin.py bootstrap_defaults:
  - [ ] Check admin existence deterministically by DEFAULT_ADMIN_EMAIL.
  - [ ] If exists: log 'Default Admin already exists.' and return without changing password.
  - [ ] If missing: require DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD; create admin user with hashed DEFAULT_ADMIN_PASSWORD.
  - [ ] Remove generate_random_password usage from bootstrap.
- [x] Verify no remaining bootstrap randomness/password logging.


- [x] Run python -m compileall app
- [x] Run uvicorn app.main:app --reload and validate first/second/third startup behavior.


