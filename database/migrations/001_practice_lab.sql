-- 001_practice_lab.sql
-- Creates tables for the Practice Lab MVP.
--
-- Idempotent: safe to re-run in most cases.
-- Rollback: see rollback section at the bottom.

BEGIN;

-- practice_topics
CREATE TABLE IF NOT EXISTS practice_topics (
    id SERIAL PRIMARY KEY,
    topic_name VARCHAR(160) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- practice_questions
CREATE TABLE IF NOT EXISTS practice_questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES practice_topics(id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(32) NOT NULL,
    starter_code TEXT NOT NULL DEFAULT '',
    expected_output TEXT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_practice_questions_topic_display_order UNIQUE (topic_id, display_order)
);



-- student_practice_progress
CREATE TABLE IF NOT EXISTS student_practice_progress (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES practice_questions(id) ON DELETE CASCADE,
    attempts_count INTEGER NOT NULL DEFAULT 0,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ NULL,
    last_attempt_at TIMESTAMPTZ NULL,
    latest_output TEXT NULL,
    latest_error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_practice_progress_student_id_question_id UNIQUE (student_id, question_id)
);

CREATE INDEX IF NOT EXISTS ix_student_practice_progress_student_id
    ON student_practice_progress(student_id);

CREATE INDEX IF NOT EXISTS ix_student_practice_progress_question_id
    ON student_practice_progress(question_id);

-- updated_at trigger (best-effort; no-op if triggers already exist)
-- PostgreSQL does not support CREATE TRIGGER IF NOT EXISTS, so we only add if absent.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_practice_topics_updated_at') THEN
        CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER set_practice_topics_updated_at
        BEFORE UPDATE ON practice_topics
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_practice_questions_updated_at') THEN
        CREATE TRIGGER set_practice_questions_updated_at
        BEFORE UPDATE ON practice_questions
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_student_practice_progress_updated_at') THEN
        CREATE TRIGGER set_student_practice_progress_updated_at
        BEFORE UPDATE ON student_practice_progress
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    END IF;
END $$;

COMMIT;

-- =====================================================
-- Rollback (manual)
-- =====================================================
-- BEGIN;
--
-- DROP TABLE IF EXISTS student_practice_progress;
-- DROP TABLE IF EXISTS practice_questions;
-- DROP TABLE IF EXISTS practice_topics;
--
-- COMMIT;

