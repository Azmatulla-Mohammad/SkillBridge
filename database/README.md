# Database Migrations

This folder contains SQL migration scripts for the SkillBridge database.

## Important
- This project currently uses `Base.metadata.create_all()` for schema creation in fresh development environments.
- For deployed PostgreSQL environments, use the SQL migrations in this folder.

## How to apply a migration
1. Locate the SQL file you need (e.g. `001_practice_lab.sql`).
2. Apply it manually using your PostgreSQL tooling:

```bash
psql "$DATABASE_URL" -f database/migrations/001_practice_lab.sql
```

(Replace with your actual connection string format.)

## Rollback
Some migrations include rollback statements in comments.

## Future Recommendation
Migrate to Alembic for automated migration tracking and rollbacks when the platform stabilizes.

