# TODO - Phase 3.1: Supabase Storage Migration

- [ ] Update `app/core/storage.py` to implement required storage abstraction:
  - [ ] Implement `upload_file(file_bytes, destination_path, content_type)`
  - [ ] Implement `download_url(path)`
  - [ ] Implement `delete_file(path)`
  - [ ] Implement `exists(path)`
  - [ ] Use official `supabase-py` client when env config exists
  - [ ] Auto-fallback to existing local storage implementation when Supabase config is missing
  - [ ] Enforce validation rules (20MB max, allowed extensions) and return friendly messages
  - [ ] Never expose Supabase exceptions to users; log failures
  - [ ] Ensure object path conventions supported by callers (materials/..., assignments/..., submissions/..., avatars/...)
  - [ ] Keep backward compatibility for existing `SupabaseStorageService().upload_file(UploadFile, folder, owner_id=...)`

- [ ] Add missing dependency to `requirements.txt` if `supabase` is not installed.

- [ ] Update all upload call sites to pass correct destination paths under the bucket structure.

- [ ] Replace any remaining direct writes to `app/static/uploads` with storage abstraction calls (if any are found).

- [ ] Run `python -m compileall app`.

- [ ] Produce PASS/FAIL report + manual testing checklist.

