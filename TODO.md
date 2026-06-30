# TODO

- [ ] Create an edit plan (no code changes yet)
- [ ] Implement fix in `app/core/config.py` only
  - [ ] Add Pydantic field alias mapping for both `auto_create_schema` and `AUTO_CREATE_SCHEMA` to same env var
  - [ ] Ensure defaults are False unless env explicitly enables
  - [ ] Add required temporary debug prints inside `get_settings()`
- [ ] Run `uvicorn app.main:app --reload` and capture startup output
- [ ] Report PASS/FAIL with explanation and exact change summary

