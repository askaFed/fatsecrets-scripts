-- Users table
CREATE TABLE IF NOT EXISTS personal_data.users (
    id SERIAL PRIMARY KEY,
    fatsecret_user_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weight history table
CREATE TABLE IF NOT EXISTS personal_data.weights (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    weight_kg NUMERIC(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Food entries (calories intake)
CREATE TABLE IF NOT EXISTS personal_data.food_entries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    meal_type TEXT,
    food_name TEXT,
    calories NUMERIC(6, 2),
    quantity NUMERIC(6, 2),
    unit TEXT,
    fatsecret_food_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exercise entries (calories burned)
CREATE TABLE IF NOT EXISTS personal_data.exercise_entries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    exercise_name TEXT,
    calories_burned NUMERIC(6, 2),
    duration_minutes NUMERIC(5, 2),
    fatsecret_exercise_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional: Daily summary view
CREATE TABLE IF NOT EXISTS personal_data.daily_summary (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    total_calories_consumed NUMERIC(6, 2),
    total_calories_burned NUMERIC(6, 2),
    weight_kg NUMERIC(5, 2),
    UNIQUE(user_id, date)
);
