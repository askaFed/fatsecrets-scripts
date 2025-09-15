-- Normalize nutrients into separate tables and migrate existing data
-- Safe to run multiple times (idempotent guards where possible)

BEGIN;

-- 1) Master list of nutrients
CREATE TABLE IF NOT EXISTS personal_data.nutrients (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,               -- e.g., vitamin_a_mcg
    display_name TEXT NOT NULL,              -- e.g., Vitamin A (mcg)
    unit TEXT NOT NULL                       -- e.g., mcg, mg, g
);

-- 2) Per-food-entry nutrient values (one row per nutrient)
CREATE TABLE IF NOT EXISTS personal_data.food_entry_nutrients (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    food_entry_id INT REFERENCES personal_data.food_entries(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    nutrient_id INT REFERENCES personal_data.nutrients(id) ON DELETE RESTRICT,
    amount DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (food_entry_id, nutrient_id)
);

-- 3) Daily nutrient goals normalized (one row per nutrient per day)
CREATE TABLE IF NOT EXISTS personal_data.daily_nutrient_goals (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    nutrient_id INT REFERENCES personal_data.nutrients(id) ON DELETE RESTRICT,
    goal_amount DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, date, nutrient_id)
);

-- 4) Seed nutrients from existing schema definitions if not already present
-- We will insert codes that match columns in estimated_food_nutrients and daily_micronutrient_goals

WITH defs AS (
    SELECT * FROM (VALUES
        ('carbohydrate_g','Carbohydrate (g)','g'),
        ('protein_g','Protein (g)','g'),
        ('fat_g','Fat (g)','g'),
        ('fiber_g','Fiber (g)','g'),
        ('vitamin_a_mcg','Vitamin A (mcg)','mcg'),
        ('vitamin_c_mg','Vitamin C (mg)','mg'),
        ('vitamin_d_mcg','Vitamin D (mcg)','mcg'),
        ('vitamin_b12_mcg','Vitamin B12 (mcg)','mcg'),
        ('calcium_mg','Calcium (mg)','mg'),
        ('iron_mg','Iron (mg)','mg'),
        ('magnesium_mg','Magnesium (mg)','mg'),
        ('potassium_mg','Potassium (mg)','mg'),
        ('zinc_mg','Zinc (mg)','mg'),
        ('selenium_mcg','Selenium (mcg)','mcg'),
        ('vitamin_k_mcg','Vitamin K (mcg)','mcg'),
        ('folate_mcg','Folate (mcg)','mcg'),
        ('inositol_mg','Inositol (mg)','mg'),
        ('thiamin_mg','Thiamin (mg)','mg'),
        ('riboflavin_mg','Riboflavin (mg)','mg'),
        ('niacin_mg','Niacin (mg)','mg'),
        ('pantothenic_acid_mg','Pantothenic Acid (mg)','mg'),
        ('vitamin_b6_mg','Vitamin B6 (mg)','mg'),
        ('biotin_mcg','Biotin (mcg)','mcg'),
        ('iodine_mcg','Iodine (mcg)','mcg'),
        ('omega_3_fatty_acids_mg','Omega-3 Fatty Acids (mg)','mg'),
        ('choline_mg','Choline (mg)','mg'),
        ('chromium_mcg','Chromium (mcg)','mcg')
    ) AS t(code, display_name, unit)
)
INSERT INTO personal_data.nutrients (code, display_name, unit)
SELECT d.code, d.display_name, d.unit
FROM defs d
LEFT JOIN personal_data.nutrients n ON n.code = d.code
WHERE n.id IS NULL;

-- 5) Backfill food_entry_nutrients from wide table personal_data.estimated_food_nutrients
DO $$
DECLARE
    rec RECORD;
    col TEXT;
    nutrient_id INT;
    amount DOUBLE PRECISION;
BEGIN
    -- Iterate over rows in estimated_food_nutrients and unpivot known columns
    FOR rec IN SELECT * FROM personal_data.estimated_food_nutrients LOOP
        -- For each nutrient code, if value is not null, insert
        FOREACH col IN ARRAY ARRAY[
            'carbohydrate_g','protein_g','fat_g','fiber_g','vitamin_a_mcg','vitamin_c_mg','vitamin_d_mcg',
            'vitamin_b12_mcg','calcium_mg','iron_mg','magnesium_mg','potassium_mg','zinc_mg','selenium_mcg',
            'vitamin_k_mcg','folate_mcg','inositol_mg','thiamin_mg','riboflavin_mg','niacin_mg','pantothenic_acid_mg',
            'vitamin_b6_mg','biotin_mcg','iodine_mcg','omega_3_fatty_acids_mg','choline_mg','chromium_mcg'
        ] LOOP
            EXECUTE format('SELECT $1.%I', col) INTO amount USING rec;
            IF amount IS NOT NULL THEN
                SELECT id INTO nutrient_id FROM personal_data.nutrients WHERE code = col;
                BEGIN
                    INSERT INTO personal_data.food_entry_nutrients (user_id, food_entry_id, date, nutrient_id, amount)
                    VALUES (COALESCE(rec.user_id, 1), rec.food_entry_id, rec.date, nutrient_id, amount)
                    ON CONFLICT (food_entry_id, nutrient_id) DO UPDATE SET amount = EXCLUDED.amount;
                EXCEPTION WHEN others THEN
                    -- ignore bad rows but continue
                    CONTINUE;
                END;
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- 6) Backfill daily_nutrient_goals from wide table personal_data.daily_micronutrient_goals
DO $$
DECLARE
    g RECORD;
    col TEXT;
    nutrient_code TEXT;
    nutrient_id INT;
    goal_value DOUBLE PRECISION;
BEGIN
    FOR g IN SELECT * FROM personal_data.daily_micronutrient_goals LOOP
        -- Map goal column names to nutrient codes used above
        FOREACH col IN ARRAY ARRAY[
            'calories_goal','protein_goal_g','carbohydrate_goal_g','fat_goal_g','fiber_goal_g',
            'vitamin_a_goal_mcg','vitamin_c_goal_mg','vitamin_d_goal_mcg','vitamin_b12_goal_mcg','calcium_goal_mg',
            'iron_goal_mg','magnesium_goal_mg','potassium_goal_mg','zinc_goal_mg','selenium_goal_mcg',
            'vitamin_k_goal_mcg','folate_goal_mcg','inositol_goal_mg','thiamin_goal_mg','riboflavin_goal_mg',
            'niacin_goal_mg','pantothenic_acid_goal_mg','vitamin_b6_goal_mg','biotin_goal_mcg','iodine_goal_mcg',
            'omega_3_fatty_acids_goal_mg','choline_goal_mg','chromium_goal_mcg'
        ] LOOP
            -- derive nutrient_code by stripping _goal* suffix and ensuring correct base code names
            nutrient_code := REPLACE(REPLACE(col, '_goal_mcg','_mcg'), '_goal_mg','_mg');
            nutrient_code := REPLACE(nutrient_code, '_goal_g','_g');
            nutrient_code := REPLACE(nutrient_code, 'calories', 'calories_kcal');
            EXECUTE format('SELECT $1.%I', col) INTO goal_value USING g;
            IF goal_value IS NOT NULL THEN
                -- only insert for nutrients that exist in master table (skip calories unless present)
                SELECT id INTO nutrient_id FROM personal_data.nutrients WHERE code = nutrient_code;
                IF nutrient_id IS NOT NULL THEN
                    INSERT INTO personal_data.daily_nutrient_goals (user_id, date, nutrient_id, goal_amount)
                    VALUES (g.user_id, g.date, nutrient_id, goal_value)
                    ON CONFLICT (user_id, date, nutrient_id) DO UPDATE SET goal_amount = EXCLUDED.goal_amount;
                END IF;
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- 7) Create or replace a new daily summary view based on normalized tables
CREATE OR REPLACE VIEW personal_data.daily_micronutrient_summary AS
WITH daily_intake AS (
    SELECT fen.user_id, fen.date, n.code, SUM(fen.amount) AS intake_value
    FROM personal_data.food_entry_nutrients fen
    JOIN personal_data.nutrients n ON n.id = fen.nutrient_id
    GROUP BY fen.user_id, fen.date, n.code
)
SELECT
    COALESCE(di.user_id, dng.user_id) AS user_id,
    COALESCE(di.date, dng.date) AS date,
    COALESCE(n.display_name, n2.display_name, di.code) AS nutrient_name,
    di.intake_value,
    dng.goal_amount AS rda_value,
    CASE WHEN dng.goal_amount IS NULL OR dng.goal_amount = 0 THEN NULL
         ELSE ROUND(((di.intake_value / dng.goal_amount) * 100)::NUMERIC, 2)
    END AS percent_of_rda,
    CASE
      WHEN dng.goal_amount IS NULL OR dng.goal_amount = 0 THEN 'NO DATA'
      WHEN di.intake_value IS NULL THEN 'No Intake Logged'
      WHEN (di.intake_value / dng.goal_amount) < 0.40 THEN 'Low'
      WHEN (di.intake_value / dng.goal_amount) < 0.60 THEN 'Fair'
      WHEN (di.intake_value / dng.goal_amount) < 0.80 THEN 'Good'
      WHEN (di.intake_value / dng.goal_amount) < 1 THEN 'Great'
      WHEN (di.intake_value / dng.goal_amount) >= 1.0 AND (di.intake_value / dng.goal_amount) < 1.25 THEN 'Excellent'
      WHEN (di.intake_value / dng.goal_amount) >= 1.25 THEN 'High'
      ELSE 'Needs Improvement'
    END AS comment
FROM daily_intake di
FULL OUTER JOIN personal_data.daily_nutrient_goals dng
  ON di.user_id = dng.user_id AND di.date = dng.date AND di.code = (SELECT code FROM personal_data.nutrients WHERE id = dng.nutrient_id)
LEFT JOIN personal_data.nutrients n ON n.code = di.code
LEFT JOIN personal_data.nutrients n2 ON n2.id = dng.nutrient_id
ORDER BY user_id, date, nutrient_name;

COMMIT;


