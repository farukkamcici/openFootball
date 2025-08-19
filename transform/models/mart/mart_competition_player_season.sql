{{ config(materialized='table') }}

WITH src AS (
    SELECT
        a.player_id,
        CASE
            WHEN p.first_name IS NULL THEN TRIM(p.last_name)
            ELSE CONCAT(TRIM(p.first_name), ' ',TRIM( p.last_name))
        END AS player_name,
        g.season,
        g.competition_id,
        a.minutes_played,
        a.goals,
        a.assists,
        a.yellow_cards,
        a.red_cards
    FROM {{ ref('stg_appearances') }} a
    INNER JOIN {{ ref('stg_players') }} p
        ON p.player_id = a.player_id
    INNER JOIN {{ ref('stg_games') }} g
        ON g.game_id = a.game_id
)

, agg AS (
    SELECT
        player_id,
        ANY_VALUE(player_name) AS player_name,
        season,
        competition_id,
        COUNT(*) AS games_played,
        SUM(minutes_played) AS minutes_played,
        SUM(goals) AS goals,
        SUM(assists) AS assists,
        SUM(yellow_cards) AS yellow_cards,
        SUM(red_cards) AS red_cards
    FROM src
    GROUP BY player_id, competition_id, season
)

, per90 AS (
    SELECT
        player_id,
        player_name,
        season,
        competition_id,
        games_played,
        minutes_played,
        goals,
        assists,
        (goals + assists) AS total_goals_and_assists,
        yellow_cards,
        red_cards,
        CASE WHEN minutes_played >= 180 THEN TRUE ELSE FALSE END AS has_180_minutes,
        CASE WHEN has_180_minutes
             THEN ROUND(goals   * 90.0 / minutes_played, 2) END AS goals_per90,
        CASE WHEN has_180_minutes
             THEN ROUND(assists * 90.0 / minutes_played, 2) END AS assists_per90,
        CASE WHEN has_180_minutes
             THEN ROUND((goals + assists) * 90.0 / minutes_played, 2) END AS goal_plus_assist_per90
    FROM agg
)


, season_vals AS (
    SELECT
        v.player_id,
        CAST(EXTRACT('year' FROM v.date) AS INT) AS season,
        v.market_value_in_eur,
        ROW_NUMBER() OVER (
            PARTITION BY v.player_id, CAST(EXTRACT('year' FROM v.date) AS INT)
            ORDER BY v.date DESC
        ) AS rn
    FROM {{ ref('stg_player_valuations') }} v
)

, season_last_valuation AS (
    SELECT
        player_id,
        season,
        market_value_in_eur AS season_last_value_eur
    FROM season_vals
    WHERE rn = 1
)

SELECT
    p.player_id,
    p.player_name,
    p.season,
    p.competition_id,
    {{ title_case ('co.competition_name') }} as competition_name,
    p.games_played,
    p.minutes_played,
    p.goals,
    p.assists,
    p.total_goals_and_assists,
    p.yellow_cards,
    p.red_cards,
    p.has_180_minutes,
    p.goals_per90,
    p.assists_per90,
    p.goal_plus_assist_per90,
    -- efficiency_score
    CASE
        WHEN has_180_minutes
        THEN ROUND(
            (p.goals_per90 * 40.0 + p.assists_per90 * 30.0 + - (p.red_cards   * 90.0 / p.minutes_played) * 10.0)
            , 3)
    END AS efficiency_score,
    lv.season_last_value_eur
FROM per90 p
LEFT JOIN season_last_valuation lv
USING (player_id, season)
LEFT JOIN {{ ref('stg_competitions') }} co
ON co.competition_id = p.competition_id
