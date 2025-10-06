-- Normalize nutrients into separate tables and migrate existing data
-- Safe to run multiple times (idempotent guards where possible)

BEGIN;

-- 1) Master list of nutrients
CREATE TABLE IF NOT EXISTS personal_data.nutrients (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,               -- e.g., vitamin_a_mcg, magnesium_mg
    category TEXT NOT NULL,           -- e.g., macronutrient, vitamin, mineral
    display_name TEXT NOT NULL,              -- e.g., Vitamin A (mcg), Magnesium (mg)
    display_name_full TEXT NOT NULL,         -- e.g., Vitamin A (mcg), Mg - Magnesium (mg)
    unit TEXT NOT NULL                       -- e.g., mcg, mg, g
);


-- 2) Daily nutrient goals normalized (one row per nutrient per day)
CREATE TABLE IF NOT EXISTS personal_data.estimated_food_nutrients_v2 (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    food_entry_id INT REFERENCES personal_data.food_entries(id),
    date DATE NOT NULL,
    meal_type TEXT,
    nutrient_id INT REFERENCES personal_data.nutrients(id) ON DELETE RESTRICT,
    amount FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 4) Seed nutrients from existing schema definitions if not already present
-- We will insert codes that match columns in estimated_food_nutrients and daily_micronutrient_goals

INSERT INTO personal_data.nutrients (code, category, display_name, display_name_full, unit)
VALUES
        -- macronutrients
        ('calories_kcal','macronutrient','Calories (kcal)','Energy - Calories (kcal)','kcal'),
        ('carbohydrate_g','macronutrient','Carbohydrate (g)','Carbohydrate (g)','g'),
        ('protein_g','macronutrient','Protein (g)','Protein (g)','g'),
        ('fat_g','macronutrient','Fat (g)','Fat (g)','g'),
        ('fiber_g','macronutrient','Fiber (g)','Dietary Fiber (g)','g'),

        -- vitamins
        ('vitamin_a_mcg','vitamin','Vitamin A (mcg)','Vitamin A (Retinol Activity Equivalents) (mcg)','mcg'),
        ('vitamin_c_mg','vitamin','Vitamin C (mg)','Vitamin C (mg)','mg'),
        ('vitamin_d_mcg','vitamin','Vitamin D (mcg)','Vitamin D (mcg)','mcg'),
        ('vitamin_k_mcg','vitamin','Vitamin K (mcg)','Vitamin K (mcg)','mcg'),

        ('thiamin_mg','vitamin','Thiamin (mg)','Vitamin B1 - Thiamin (mg)','mg'),
        ('riboflavin_mg','vitamin','Riboflavin (mg)','Vitamin B2 - Riboflavin (mg)','mg'),
        ('niacin_mg','vitamin','Niacin (mg)','Vitamin B3 - Niacin (mg)','mg'),
        ('choline_mg','vitamin','Choline (mg)','Vitamin B4 - Choline (mg)','mg'),
        ('pantothenic_acid_mg','vitamin','Pantothenic Acid (mg)','Vitamin B5 - Pantothenic Acid (mg)','mg'),
        ('vitamin_b6_mg','vitamin','Vitamin B6 (mg)','Vitamin B6 (mg)','mg'),
        ('biotin_mcg','vitamin','Biotin (mcg)','Biotin (Vitamin B7) (mcg)','mcg'),
        ('inositol_mg','vitamin','Inositol (mg)','Vitamin B8 - Inositol (mg)','mg'),
        ('folate_mcg','vitamin','Folate (mcg)','Vitamin B9 - Folate (DFE) (mcg)','mcg'),
        ('vitamin_b12_mcg','vitamin','Vitamin B12 (mcg)','Vitamin B12 (Cobalamin) (mcg)','mcg'),

        -- minerals
        ('calcium_mg','mineral','Calcium (mg)','Calcium (mg)','mg'),
        ('iron_mg','mineral','Iron (mg)','Iron (mg)','mg'),
        ('magnesium_mg','mineral','Magnesium (mg)','Magnesium (mg)','mg'),
        ('potassium_mg','mineral','Potassium (mg)','Potassium (mg)','mg'),
        ('zinc_mg','mineral','Zinc (mg)','Zinc (mg)','mg'),
        ('selenium_mcg','mineral','Selenium (mcg)','Selenium (mcg)','mcg'),
        ('iodine_mcg','mineral','Iodine (mcg)','Iodine (mcg)','mcg'),
        ('chromium_mcg','mineral','Chromium (mcg)','Chromium (mcg)','mcg'),

        -- other nutrients
        ('omega_3_fatty_acids_mg','fats','Omega-3 Fatty Acids (mg)','Omega-3 Fatty Acids (mg)','mg')
ON CONFLICT (code) DO NOTHING;



select * from personal_data.nutrients ;

-- Step 3: Migrate data using UNPIVOT-like approach with UNION ALL
INSERT INTO personal_data.estimated_food_nutrients_v2 (
    user_id, food_entry_id, date, meal_type, nutrient_id, amount, created_at
)
SELECT
    user_id,
    food_entry_id,
    date,
    meal_type,
    n.id as nutrient_id,
    amount,
    created_at
FROM (
    -- Carbohydrate
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'carbohydrate_g' as nutrient_code, carbohydrate_g as amount
    FROM personal_data.estimated_food_nutrients WHERE carbohydrate_g IS NOT NULL

    UNION ALL

    -- Protein
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'protein_g', protein_g
    FROM personal_data.estimated_food_nutrients WHERE protein_g IS NOT NULL

    UNION ALL

    -- Fat
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'fat_g', fat_g
    FROM personal_data.estimated_food_nutrients WHERE fat_g IS NOT NULL

    UNION ALL

    -- Fiber
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'fiber_g', fiber_g
    FROM personal_data.estimated_food_nutrients WHERE fiber_g IS NOT NULL

    UNION ALL

    -- Vitamin A
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_a_mcg', vitamin_a_mcg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_a_mcg IS NOT NULL

    UNION ALL

    -- Vitamin C
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_c_mg', vitamin_c_mg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_c_mg IS NOT NULL

    UNION ALL

    -- Vitamin D
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_d_mcg', vitamin_d_mcg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_d_mcg IS NOT NULL

    UNION ALL

    -- Vitamin B12
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_b12_mcg', vitamin_b12_mcg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_b12_mcg IS NOT NULL

    UNION ALL

    -- Calcium
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'calcium_mg', calcium_mg
    FROM personal_data.estimated_food_nutrients WHERE calcium_mg IS NOT NULL

    UNION ALL

    -- Iron
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'iron_mg', iron_mg
    FROM personal_data.estimated_food_nutrients WHERE iron_mg IS NOT NULL

    UNION ALL

    -- Magnesium
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'magnesium_mg', magnesium_mg
    FROM personal_data.estimated_food_nutrients WHERE magnesium_mg IS NOT NULL

    UNION ALL

    -- Potassium
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'potassium_mg', potassium_mg
    FROM personal_data.estimated_food_nutrients WHERE potassium_mg IS NOT NULL

    UNION ALL

    -- Zinc
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'zinc_mg', zinc_mg
    FROM personal_data.estimated_food_nutrients WHERE zinc_mg IS NOT NULL

    UNION ALL

    -- Selenium
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'selenium_mcg', selenium_mcg
    FROM personal_data.estimated_food_nutrients WHERE selenium_mcg IS NOT NULL

    UNION ALL

    -- Vitamin K
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_k_mcg', vitamin_k_mcg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_k_mcg IS NOT NULL

    UNION ALL

    -- Folate
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'folate_mcg', folate_mcg
    FROM personal_data.estimated_food_nutrients WHERE folate_mcg IS NOT NULL

    UNION ALL

    -- Inositol
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'inositol_mg', inositol_mg
    FROM personal_data.estimated_food_nutrients WHERE inositol_mg IS NOT NULL

    UNION ALL

    -- Thiamin
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'thiamin_mg', thiamin_mg
    FROM personal_data.estimated_food_nutrients WHERE thiamin_mg IS NOT NULL

    UNION ALL

    -- Riboflavin
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'riboflavin_mg', riboflavin_mg
    FROM personal_data.estimated_food_nutrients WHERE riboflavin_mg IS NOT NULL

    UNION ALL

    -- Niacin
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'niacin_mg', niacin_mg
    FROM personal_data.estimated_food_nutrients WHERE niacin_mg IS NOT NULL

    UNION ALL

    -- Pantothenic Acid
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'pantothenic_acid_mg', pantothenic_acid_mg
    FROM personal_data.estimated_food_nutrients WHERE pantothenic_acid_mg IS NOT NULL

    UNION ALL

    -- Vitamin B6
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'vitamin_b6_mg', vitamin_b6_mg
    FROM personal_data.estimated_food_nutrients WHERE vitamin_b6_mg IS NOT NULL

    UNION ALL

    -- Biotin
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'biotin_mcg', biotin_mcg
    FROM personal_data.estimated_food_nutrients WHERE biotin_mcg IS NOT NULL

    UNION ALL

    -- Iodine
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'iodine_mcg', iodine_mcg
    FROM personal_data.estimated_food_nutrients WHERE iodine_mcg IS NOT NULL

    UNION ALL

    -- Omega-3 Fatty Acids
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'omega_3_fatty_acids_mg', omega_3_fatty_acids_mg
    FROM personal_data.estimated_food_nutrients WHERE omega_3_fatty_acids_mg IS NOT NULL

    UNION ALL

    -- Choline
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'choline_mg', choline_mg
    FROM personal_data.estimated_food_nutrients WHERE choline_mg IS NOT NULL

    UNION ALL

    -- Chromium
    SELECT user_id, food_entry_id, date, meal_type, created_at, 'chromium_mcg', chromium_mcg
    FROM personal_data.estimated_food_nutrients WHERE chromium_mcg IS NOT NULL

) unpivoted_data
JOIN personal_data.nutrients n ON n.code = unpivoted_data.nutrient_code;

-- Step 5: Verify the migration (optional)
-- Compare record counts
SELECT 'Original table count' as description, COUNT(*) as count FROM personal_data.estimated_food_nutrients
UNION ALL
SELECT 'New table food entries', COUNT(DISTINCT food_entry_id) FROM personal_data.estimated_food_nutrients_v2
UNION ALL
SELECT 'New table total records', COUNT(*) FROM personal_data.estimated_food_nutrients_v2;

-- Sample query to verify data integrity
SELECT
    efn_old.food_entry_id,
    efn_old.protein_g as old_protein,
    efn_v2.amount as new_protein
FROM personal_data.estimated_food_nutrients efn_old
JOIN personal_data.estimated_food_nutrients_v2 efn_v2 ON efn_old.food_entry_id = efn_v2.food_entry_id
JOIN personal_data.nutrients n ON efn_v2.nutrient_id = n.id
WHERE n.code = 'protein_g'
AND efn_old.protein_g IS NOT NULL
LIMIT 5;