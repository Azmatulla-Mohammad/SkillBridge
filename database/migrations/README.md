# Migration scripts (SQL)

This folder contains idempotent SQL migrations for the SkillBridge database.

## 001_practice_lab.sql
Creates the following new tables:
- `practice_topics`
- `practice_questions`
- `student_practice_progress`

### Apply manually
Use your PostgreSQL tooling, e.g.:

```bash
psql "$DATABASE_URL" -f database/migrations/001_practice_lab.sql
```

## Rollback
Rollback statements are included at the bottom of each SQL file as comments.

## Future Recommendation
Adopt Alembic when the product stabilizes for automated migration tracking.

