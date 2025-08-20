{{ config(materialized='table') }}

WITH src AS (
    SELECT
        player_id,
        date,
        market_value_in_eur AS market_value
    FROM {{ ref('stg_player_valuations') }}
)

, seasoned AS (
    SELECT
        player_id,
        date,
        CASE
          WHEN EXTRACT(MONTH FROM s.date) >= 7
            THEN CONCAT(EXTRACT(YEAR FROM s.date), '/', EXTRACT(YEAR FROM s.date) + 1)
          ELSE CONCAT(EXTRACT(YEAR FROM s.date) - 1, '/', EXTRACT(YEAR FROM s.date))
        END AS season,
        market_value,
        ROW_NUMBER() OVER(PARTITION BY player_id, season ORDER BY date ASC) AS rn_asc,
        ROW_NUMBER() OVER(PARTITION BY player_id, season ORDER BY date DESC) AS rn_desc
    FROM src s
)

, agg AS (
    SELECT
        player_id,
        season,
        MAX(CASE WHEN rn_asc = 1 THEN market_value END) AS first_market_value,
        MAX(CASE WHEN rn_desc = 1 THEN market_value END) AS last_market_value,
        MIN(market_value) AS min_market_value,
        MAX(market_value) AS max_market_value
    FROM seasoned
    GROUP BY player_id, season
)

, diff_calc AS (
        SELECT
            *,
            (last_market_value - first_market_value) AS value_change_amount,
            ROUND((last_market_value - first_market_value) / NULLIF(first_market_value, 0) * 100, 2) AS value_change_percentage,
        FROM agg a
)

SELECT
    d.player_id,
    p.name,
    d.season,
    d.first_market_value,
    d.last_market_value,
    d.min_market_value,
    d.max_market_value,
    d.value_change_amount,
    d.value_change_percentage
FROM diff_calc d
INNER JOIN {{ ref('stg_players') }} p
ON d.player_id = p.player_id
