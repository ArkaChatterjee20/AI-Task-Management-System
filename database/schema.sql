
-- =====================================================
-- AI TASK MANAGEMENT SYSTEM
-- PostgreSQL Operational Database Schema
-- =====================================================

-- 1. APPLICATION USERS
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. APPLICATION TASKS
CREATE TABLE IF NOT EXISTS tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_title TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tasks_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_task_title
        CHECK (LENGTH(TRIM(task_title)) > 0)
);

-- 3. EXTERNAL TASKS (JSONPlaceholder imports)
CREATE TABLE IF NOT EXISTS external_tasks (
    source_task_id BIGINT PRIMARY KEY,
    source_user_id BIGINT NOT NULL,
    task_title TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. INDEXES

-- Efficient user-specific task retrieval and pagination
CREATE INDEX IF NOT EXISTS idx_tasks_user_created
    ON tasks(user_id, created_at DESC, task_id DESC);

-- Efficient external task lookup by source user
CREATE INDEX IF NOT EXISTS idx_external_tasks_source_user
    ON external_tasks(source_user_id);