-- Daily micronutrient goals table
CREATE TABLE IF NOT EXISTS personal_data.daily_micronutrient_goals_v2 (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES personal_data.users(id),
    date DATE NOT NULL,
    nutrient_id INT REFERENCES personal_data.nutrients(id),
    goal_value FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, date, nutrient_id)
)

-- Step 2: Migrate data from old goals table to new normalized structure
INSERT INTO personal_data.daily_micronutrient_goals_v2 (user_id, date, nutrient_id, goal_value, created_at, updated_at)
SELECT
    user_id,
    date,
    n.id as nutrient_id,
    goal_value,
    COALESCE(created_at, NOW()) as created_at,
    COALESCE(created_at, NOW()) as updated_at
FROM (
    -- Vitamin A
    SELECT user_id, date, created_at, 'vitamin_a_mcg' as nutrient_code, vitamin_a_goal_mcg as goal_value
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_a_goal_mcg IS NOT NULL

    UNION ALL

    -- Vitamin C
    SELECT user_id, date, created_at, 'vitamin_c_mg', vitamin_c_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_c_goal_mg IS NOT NULL

    UNION ALL

    -- Vitamin D
    SELECT user_id, date, created_at, 'vitamin_d_mcg', vitamin_d_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_d_goal_mcg IS NOT NULL

    UNION ALL

    -- Vitamin B12
    SELECT user_id, date, created_at,  'vitamin_b12_mcg', vitamin_b12_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_b12_goal_mcg IS NOT NULL

    UNION ALL

    -- Calcium
    SELECT user_id, date, created_at,  'calcium_mg', calcium_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE calcium_goal_mg IS NOT NULL

    UNION ALL

    -- Iron
    SELECT user_id, date, created_at,  'iron_mg', iron_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE iron_goal_mg IS NOT NULL

    UNION ALL

    -- Magnesium
    SELECT user_id, date, created_at,  'magnesium_mg', magnesium_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE magnesium_goal_mg IS NOT NULL

    UNION ALL

    -- Potassium
    SELECT user_id, date, created_at, 'potassium_mg', potassium_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE potassium_goal_mg IS NOT NULL

    UNION ALL

    -- Zinc
    SELECT user_id, date, created_at, 'zinc_mg', zinc_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE zinc_goal_mg IS NOT NULL

    UNION ALL

    -- Selenium
    SELECT user_id, date, created_at,  'selenium_mcg', selenium_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE selenium_goal_mcg IS NOT NULL

    UNION ALL

    -- Vitamin K
    SELECT user_id, date, created_at,  'vitamin_k_mcg', vitamin_k_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_k_goal_mcg IS NOT NULL

    UNION ALL

    -- Folate
    SELECT user_id, date, created_at,  'folate_mcg', folate_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE folate_goal_mcg IS NOT NULL

    UNION ALL

    -- Inositol
    SELECT user_id, date, created_at, 'inositol_mg', inositol_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE inositol_goal_mg IS NOT NULL

    UNION ALL

    -- Thiamin
    SELECT user_id, date, created_at,  'thiamin_mg', thiamin_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE thiamin_goal_mg IS NOT NULL

    UNION ALL

    -- Riboflavin
    SELECT user_id, date, created_at,  'riboflavin_mg', riboflavin_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE riboflavin_goal_mg IS NOT NULL

    UNION ALL

    -- Niacin
    SELECT user_id, date, created_at,  'niacin_mg', niacin_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE niacin_goal_mg IS NOT NULL

    UNION ALL

    -- Pantothenic Acid
    SELECT user_id, date, created_at, 'pantothenic_acid_mg', pantothenic_acid_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE pantothenic_acid_goal_mg IS NOT NULL

    UNION ALL

    -- Vitamin B6
    SELECT user_id, date, created_at,  'vitamin_b6_mg', vitamin_b6_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE vitamin_b6_goal_mg IS NOT NULL

    UNION ALL

    -- Biotin
    SELECT user_id, date, created_at,  'biotin_mcg', biotin_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE biotin_goal_mcg IS NOT NULL

    UNION ALL

    -- Iodine
    SELECT user_id, date, created_at,  'iodine_mcg', iodine_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE iodine_goal_mcg IS NOT NULL

    UNION ALL

    -- Omega-3 Fatty Acids
    SELECT user_id, date, created_at, 'omega_3_fatty_acids_mg', omega_3_fatty_acids_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE omega_3_fatty_acids_goal_mg IS NOT NULL

    UNION ALL

    -- Choline
    SELECT user_id, date, created_at,  'choline_mg', choline_goal_mg
    FROM personal_data.daily_micronutrient_goals WHERE choline_goal_mg IS NOT NULL

    UNION ALL

    -- Chromium
    SELECT user_id, date, created_at,  'chromium_mcg', chromium_goal_mcg
    FROM personal_data.daily_micronutrient_goals WHERE chromium_goal_mcg IS NOT NULL

) unpivoted_goals
JOIN personal_data.nutrients n ON n.code = unpivoted_goals.nutrient_code
ON CONFLICT (user_id, date, nutrient_id) DO NOTHING;
