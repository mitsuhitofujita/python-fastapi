-- Create test database for automated testing
CREATE DATABASE app_test;

-- Create test user
CREATE USER app_test WITH PASSWORD 'app_test';

-- Grant privileges to test user
GRANT ALL PRIVILEGES ON DATABASE app_test TO app_test;
