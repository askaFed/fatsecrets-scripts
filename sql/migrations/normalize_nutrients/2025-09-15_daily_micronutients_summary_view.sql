CREATE OR REPLACE VIEW personal_data.daily_micronutrient_summary_v2 AS
WITH
  daily_intake AS (
    SELECT
      efn.user_id,
      efn.date,
      efn.nutrient_id,
      n.display_name AS nutrient_name,
      SUM(efn.amount) AS intake_value
    FROM
      personal_data.estimated_food_nutrients_v2 efn
      JOIN personal_data.nutrients n ON efn.nutrient_id = n.id
    GROUP BY
      efn.user_id,
      efn.date,
      efn.nutrient_id,
      n.display_name
  )

SELECT
  COALESCE(di.user_id, g.user_id) AS user_id,
  COALESCE(di.date, g.date) AS date,
  COALESCE(di.nutrient_name, n.display_name) AS nutrient_name,
  COALESCE(di.intake_value, 0) AS intake_value,
  COALESCE(g.goal_value, 0) AS rda_value,
  CASE
    WHEN g.goal_value IS NULL OR g.goal_value = 0
    THEN NULL
    ELSE ROUND(((di.intake_value / g.goal_value) * 100)::NUMERIC, 2)
  END AS percent_of_rda,
  CASE
    WHEN g.goal_value IS NULL OR g.goal_value = 0
    THEN 'NO DATA'
    WHEN di.intake_value IS NULL
    THEN 'No Intake Logged'
    WHEN (di.intake_value / g.goal_value) < 0.40
    THEN 'Low'
    WHEN (di.intake_value / g.goal_value) < 0.60
    THEN 'Fair'
    WHEN (di.intake_value / g.goal_value) < 0.80
    THEN 'Good'
    WHEN (di.intake_value / g.goal_value) < 1
    THEN 'Great'
    WHEN (di.intake_value / g.goal_value) >= 1.0 AND (di.intake_value / g.goal_value) < 1.25
    THEN 'Excellent'
    WHEN (di.intake_value / g.goal_value) >= 1.25
    THEN 'High'
    ELSE 'Needs Improvement'
  END AS comment
FROM
  daily_intake di
  FULL OUTER JOIN personal_data.daily_micronutrient_goals_v2 g
    ON di.user_id = g.user_id
    --AND di.date = g.date
    AND di.nutrient_id = g.nutrient_id
  LEFT JOIN personal_data.nutrients n ON COALESCE(di.nutrient_id, g.nutrient_id) = n.id
ORDER BY
  user_id,
  date,
  nutrient_name;

-- Test the view with a sample query
SELECT * FROM personal_data.daily_micronutrient_summary_v2
WHERE user_id = 1
ORDER BY date DESC, nutrient_name
LIMIT 10;

