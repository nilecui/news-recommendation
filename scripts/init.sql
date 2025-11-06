-- Initialize PostgreSQL database for news recommendation system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for full-text search
-- These will be created after tables are created