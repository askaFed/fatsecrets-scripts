-- Users table
CREATE TABLE IF NOT EXISTS personal_data.users (
    id SERIAL PRIMARY KEY,
    fatsecret_user_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Access tokens table
CREATE TABLE IF NOT EXISTS personal_data.access_tokens (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    access_token TEXT NOT NULL,
    access_token_secret TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
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
-- Updated Food entries table
-- Updated Food entries table
CREATE TABLE IF NOT EXISTS personal_data.food_entries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    meal_type TEXT,
    food_name TEXT,
    calories NUMERIC(6, 2),
    carbohydrate NUMERIC(6, 2),
    protein NUMERIC(6, 2),
    fat NUMERIC(6, 2),
    saturated_fat NUMERIC(6, 2),
    sugar NUMERIC(6, 2),
    fiber NUMERIC(6, 2),
    calcium NUMERIC(6, 2),
    iron NUMERIC(6, 2),
    cholesterol NUMERIC(6, 2),
    sodium NUMERIC(6, 2),
    vitamin_a NUMERIC(6, 2),
    vitamin_c NUMERIC(6, 2),
    monounsaturated_fat NUMERIC(6, 3),
    polyunsaturated_fat NUMERIC(6, 3),
    quantity NUMERIC(6, 2),
    unit TEXT,
    fatsecret_food_id TEXT,
    fatsecret_food_entry_id TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Exercise entries (calories burned)
CREATE TABLE IF NOT EXISTS personal_data.exercise_entries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    exercise_name TEXT,
    calories NUMERIC(8, 2),
    duration_minutes NUMERIC(8, 2),
    fatsecret_exercise_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, date, fatsecret_exercise_id)
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

CREATE TABLE  IF NOT EXISTS personal_data.estimated_food_nutrients (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id) DEFAULT 1,
    food_entry_id INT UNIQUE REFERENCES personal_data.food_entries,
    date DATE NOT NULL,
    meal_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    carbohydrate_g FLOAT,
    protein_g FLOAT,
    fat_g FLOAT,
    fiber_g FLOAT,
    vitamin_a_mcg FLOAT,
    vitamin_c_mg FLOAT,
    vitamin_d_mcg FLOAT,
    vitamin_b12_mcg FLOAT,
    calcium_mg FLOAT,
    iron_mg FLOAT,
    magnesium_mg FLOAT,
    potassium_mg FLOAT,
    zinc_mg FLOAT,
    selenium_mcg FLOAT,
    vitamin_k_mcg FLOAT,
    folate_mcg FLOAT,
    inositol_mg FLOAT,
    thiamin_mg FLOAT,
    riboflavin_mg FLOAT,
    niacin_mg FLOAT,
    pantothenic_acid_mg FLOAT,
    vitamin_b6_mg FLOAT,
    biotin_mcg FLOAT,
    iodine_mcg FLOAT,
    omega_3_fatty_acids_mg FLOAT,
    choline_mg FLOAT,
    chromium_mcg FLOAT
);

