-- Migration: Add allure_uuid column to test_results table
-- Run this SQL directly on your PostgreSQL database

-- Step 1: Add column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_results' AND column_name = 'allure_uuid'
    ) THEN
        ALTER TABLE test_results ADD COLUMN allure_uuid VARCHAR(255);
        RAISE NOTICE 'Column allure_uuid added successfully';
    ELSE
        RAISE NOTICE 'Column allure_uuid already exists';
    END IF;
END $$;

-- Step 2: Create index (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'test_results' AND indexname = 'ix_test_results_allure_uuid'
    ) THEN
        CREATE INDEX ix_test_results_allure_uuid ON test_results(allure_uuid);
        RAISE NOTICE 'Index ix_test_results_allure_uuid created successfully';
    ELSE
        RAISE NOTICE 'Index ix_test_results_allure_uuid already exists';
    END IF;
END $$;

-- Verify migration
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'test_results' AND column_name = 'allure_uuid';

SELECT 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename = 'test_results' AND indexname = 'ix_test_results_allure_uuid';

