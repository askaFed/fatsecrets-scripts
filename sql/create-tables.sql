-- Users table
CREATE TABLE IF NOT EXISTS personal_data.users (
    id SERIAL PRIMARY KEY,
    fatsecret_user_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User details table for demographic information
CREATE TABLE IF NOT EXISTS personal_data.user_details (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id) UNIQUE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    age INTEGER CHECK (age > 0 AND age < 150),
    weight_kg NUMERIC(5, 2),
    height_cm NUMERIC(5, 2),
    activity_level TEXT CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active')),
    pregnancy_status TEXT CHECK (pregnancy_status IN ('not_pregnant', 'pregnant', 'breastfeeding')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily micronutrient goals table
CREATE TABLE IF NOT EXISTS personal_data.daily_micronutrient_goals (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Macronutrients
    calories_goal NUMERIC(6, 2),
    protein_goal_g NUMERIC(6, 2),
    carbohydrate_goal_g NUMERIC(6, 2),
    fat_goal_g NUMERIC(6, 2),
    fiber_goal_g NUMERIC(6, 2),
    -- Micronutrients
    vitamin_a_goal_mcg NUMERIC(8, 2),
    vitamin_c_goal_mg NUMERIC(8, 2),
    vitamin_d_goal_mcg NUMERIC(8, 2),
    vitamin_b12_goal_mcg NUMERIC(8, 2),
    calcium_goal_mg NUMERIC(8, 2),
    iron_goal_mg NUMERIC(8, 2),
    magnesium_goal_mg NUMERIC(8, 2),
    potassium_goal_mg NUMERIC(8, 2),
    zinc_goal_mg NUMERIC(8, 2),
    selenium_goal_mcg NUMERIC(8, 2),
    vitamin_k_goal_mcg NUMERIC(8, 2),
    folate_goal_mcg NUMERIC(8, 2),
    inositol_goal_mg NUMERIC(8, 2),
    thiamin_goal_mg NUMERIC(8, 2),
    riboflavin_goal_mg NUMERIC(8, 2),
    niacin_goal_mg NUMERIC(8, 2),
    pantothenic_acid_goal_mg NUMERIC(8, 2),
    vitamin_b6_goal_mg NUMERIC(8, 2),
    biotin_goal_mcg NUMERIC(8, 2),
    iodine_goal_mcg NUMERIC(8, 2),
    omega_3_fatty_acids_goal_mg NUMERIC(8, 2),
    choline_goal_mg NUMERIC(8, 2),
    chromium_goal_mcg NUMERIC(8, 2),
    UNIQUE(user_id, date)
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

