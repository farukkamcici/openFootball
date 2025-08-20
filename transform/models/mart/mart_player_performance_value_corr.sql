{{ config(materialized='table') }}

WITH perf AS (
    SELECT
        player_id,
        season,
        player_name,
        minutes_played,
        goals_per90,
        assists_per90,
        goal_plus_assist_per90,
        efficiency_score
    FROM {{ ref('mart_player_season') }}
),

val AS (
    SELECT
        player_id,
        season,
        first_market_value,
        last_market_value,
        value_change_amount,
        value_change_percentage
    FROM {{ ref('mart_player_valuation_season') }}
),

player AS (
    SELECT
        player_id,
        date_of_birth
    FROM {{ ref('stg_players') }}
)

SELECT
    perf.player_id,
    perf.player_name,
    DATE_DIFF(
        'year',
        player.date_of_birth,
        MAKE_DATE(CAST(perf.season AS INTEGER), 6, 30)
    ) AS age_in_season,
    perf.season,
    perf.minutes_played,
    perf.goals_per90,
    perf.assists_per90,
    perf.goal_plus_assist_per90,
    perf.efficiency_score,
    val.first_market_value,
    val.last_market_value,
    val.value_change_amount,
    val.value_change_percentage
FROM perf
LEFT JOIN val
  ON perf.player_id = val.player_id
 AND perf.season = LEFT(val.season, 4)
LEFT JOIN player
  ON perf.player_id = player.player_id
