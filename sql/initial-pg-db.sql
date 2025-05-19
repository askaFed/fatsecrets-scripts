-- Run this as ADMIN user

-- Step 1: Create the database
CREATE DATABASE fatsecrets_db;

-- Step 2: Create the user with a password
CREATE USER fatsecrets_intergration WITH PASSWORD 'fatsecrets_intergration_pwd';

-- Step 3: Grant connect privileges on the database
GRANT ALL PRIVILEGES ON DATABASE fatsecrets_db TO fatsecrets_intergration;

-- Run this as ADMIN user and connect to fatsecrets_db

CREATE SCHEMA IF NOT EXISTS personal_data;
CREATE SCHEMA IF NOT EXISTS public_data;

GRANT ALL PRIVILEGES ON SCHEMA personal_data TO fatsecrets_intergration;
GRANT ALL PRIVILEGES ON SCHEMA public_data TO fatsecrets_intergration;