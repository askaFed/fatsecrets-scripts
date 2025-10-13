
CREATE OR REPLACE VIEW personal_data.daily_micronutrient_summary AS
WITH
  daily_intake AS (
    SELECT
      n.user_id,
      n.date,
      SUM(vitamin_a_mcg) AS vitamin_a_mcg,
      SUM(vitamin_c_mg) AS vitamin_c_mg,
      SUM(vitamin_d_mcg) AS vitamin_d_mcg,
      SUM(vitamin_b12_mcg) AS vitamin_b12_mcg,
      SUM(calcium_mg) AS calcium_mg,
      SUM(iron_mg) AS iron_mg,
      SUM(magnesium_mg) AS magnesium_mg,
      SUM(potassium_mg) AS potassium_mg,
      SUM(zinc_mg) AS zinc_mg,
      SUM(selenium_mcg) AS selenium_mcg,
      SUM(vitamin_k_mcg) AS vitamin_k_mcg,
      SUM(folate_mcg) AS folate_mcg,
      SUM(inositol_mg) AS inositol_mg,
      SUM(thiamin_mg) AS thiamin_mg,
      SUM(riboflavin_mg) AS riboflavin_mg,
      SUM(niacin_mg) AS niacin_mg,
      SUM(pantothenic_acid_mg) AS pantothenic_acid_mg,
      SUM(vitamin_b6_mg) AS vitamin_b6_mg,
      SUM(biotin_mcg) AS biotin_mcg,
      SUM(iodine_mcg) AS iodine_mcg,
      SUM(omega_3_fatty_acids_mg) AS omega_3_fatty_acids_mg,
      SUM(choline_mg) AS choline_mg,
      SUM(chromium_mcg) AS chromium_mcg
    FROM
      personal_data.estimated_food_nutrients n
  LEFT JOIN personal_data.date_exclusions de
    ON de.user_id = n.user_id
   AND de.date = n.date
  WHERE de.id IS NULL
    GROUP BY
      n.user_id,
      n.date
  )

SELECT
  user_id,
  date,
  nutrient_name,
  COALESCE(intake_value, 0) AS intake_value,
  COALESCE(rda_value, 0) AS rda_value,
  CASE
    WHEN rda_value IS NULL OR rda_value = 0
    THEN NULL
    ELSE ROUND(((intake_value / rda_value) * 100)::NUMERIC, 2)
  END AS percent_of_rda,
  CASE
    WHEN rda_value IS NULL OR rda_value = 0
    THEN 'NO DATA'
    WHEN intake_value IS NULL
    THEN 'No Intake Logged'
    WHEN (intake_value / rda_value) < 0.40
    THEN 'Low'
    WHEN (intake_value / rda_value) < 0.60
    THEN 'Fair'
    WHEN (intake_value / rda_value) < 0.80
    THEN 'Good'
    WHEN (intake_value / rda_value) < 1
    THEN 'Great'
    WHEN (intake_value / rda_value) >= 1.0  AND (intake_value / rda_value) < 1.25
    THEN 'Excellent'
    WHEN (intake_value / rda_value) >= 1.25
    THEN 'High'
    ELSE 'Needs Improvement'
  END AS comment
FROM
  (
    -- Use a FULL OUTER JOIN on daily intake and goals to ensure all days and users are included
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin A (mcg)' AS nutrient_name,
      di.vitamin_a_mcg AS intake_value,
      dmg.vitamin_a_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin C (mg)' AS nutrient_name,
      di.vitamin_c_mg AS intake_value,
      dmg.vitamin_c_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin D (mcg)' AS nutrient_name,
      di.vitamin_d_mcg AS intake_value,
      dmg.vitamin_d_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin B12 (mcg)' AS nutrient_name,
      di.vitamin_b12_mcg AS intake_value,
      dmg.vitamin_b12_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Calcium (mg)' AS nutrient_name,
      di.calcium_mg AS intake_value,
      dmg.calcium_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Iron (mg)' AS nutrient_name,
      di.iron_mg AS intake_value,
      dmg.iron_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Magnesium (mg)' AS nutrient_name,
      di.magnesium_mg AS intake_value,
      dmg.magnesium_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Potassium (mg)' AS nutrient_name,
      di.potassium_mg AS intake_value,
      dmg.potassium_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Zinc (mg)' AS nutrient_name,
      di.zinc_mg AS intake_value,
      dmg.zinc_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Selenium (mcg)' AS nutrient_name,
      di.selenium_mcg AS intake_value,
      dmg.selenium_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin K (mcg)' AS nutrient_name,
      di.vitamin_k_mcg AS intake_value,
      dmg.vitamin_k_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Folate (mcg)' AS nutrient_name,
      di.folate_mcg AS intake_value,
      dmg.folate_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Inositol (mg)' AS nutrient_name,
      di.inositol_mg AS intake_value,
      dmg.inositol_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Thiamin (mg)' AS nutrient_name,
      di.thiamin_mg AS intake_value,
      dmg.thiamin_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Riboflavin (mg)' AS nutrient_name,
      di.riboflavin_mg AS intake_value,
      dmg.riboflavin_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Niacin (mg)' AS nutrient_name,
      di.niacin_mg AS intake_value,
      dmg.niacin_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Pantothenic Acid (mg)' AS nutrient_name,
      di.pantothenic_acid_mg AS intake_value,
      dmg.pantothenic_acid_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Vitamin B6 (mg)' AS nutrient_name,
      di.vitamin_b6_mg AS intake_value,
      dmg.vitamin_b6_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Biotin (mcg)' AS nutrient_name,
      di.biotin_mcg AS intake_value,
      dmg.biotin_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Iodine (mcg)' AS nutrient_name,
      di.iodine_mcg AS intake_value,
      dmg.iodine_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Omega-3 Fatty Acids (mg)' AS nutrient_name,
      di.omega_3_fatty_acids_mg AS intake_value,
      dmg.omega_3_fatty_acids_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Choline (mg)' AS nutrient_name,
      di.choline_mg AS intake_value,
      dmg.choline_goal_mg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
    UNION
    ALL
    SELECT
      COALESCE(di.user_id, dmg.user_id) AS user_id,
      COALESCE(di.date, dmg.date) AS date,
      'Chromium (mcg)' AS nutrient_name,
      di.chromium_mcg AS intake_value,
      dmg.chromium_goal_mcg AS rda_value
    FROM
      daily_intake AS di FULL
      OUTER JOIN personal_data.daily_micronutrient_goals AS dmg ON di.user_id = dmg.user_id
  ) AS unpivoted_data
ORDER BY
  user_id,
  date,
  nutrient_name;
