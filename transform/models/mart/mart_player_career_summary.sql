{{ config(materialized='table') }}

-- career summary merged with player metadata
WITH base_perf AS (
    SELECT
        a.player_id,
        COUNT(DISTINCT a.game_id) AS total_matches,
        SUM(a.minutes_played)     AS total_minutes,
        SUM(a.goals)              AS total_goals,
        SUM(a.assists)            AS total_assists,
        SUM(a.yellow_cards)       AS total_yellow_cards,
        SUM(a.red_cards)          AS total_red_cards
    FROM {{ ref('stg_appearances') }} a
    GROUP BY a.player_id
),

players AS (
    SELECT
        p.player_id,
        p.name AS player_name,
        p.date_of_birth,
        p.country_of_citizenship,
        p.foot,
        p.position,
        p.sub_position,
        p.highest_market_value_in_eur  AS career_peak_value_eur,
        p.last_season,
    FROM {{ ref('stg_players') }} p
)

SELECT
    pl.player_id,
    pl.player_name,
    pl.date_of_birth,
    pl.country_of_citizenship,
    pl.foot,
    pl.position,
    pl.sub_position,
    pl.career_peak_value_eur,
    pl.last_season,
    COALESCE(bp.total_matches, 0)       AS total_matches,
    COALESCE(bp.total_minutes, 0)       AS total_minutes,
    COALESCE(bp.total_goals, 0)         AS total_goals,
    COALESCE(bp.total_assists, 0)       AS total_assists,
    COALESCE(bp.total_goals, 0) + COALESCE(bp.total_assists, 0)       AS total_goal_contributions,
    COALESCE(bp.total_yellow_cards, 0)  AS total_yellow_cards,
    COALESCE(bp.total_red_cards, 0)     AS total_red_cards,
    ROUND(bp.total_goals/NULLIF(bp.total_matches, 0) ,2) AS gpg,
    ROUND(bp.total_assists/NULLIF(bp.total_matches, 0) ,2) AS apg,
    ROUND((bp.total_assists + bp.total_goals)/NULLIF(bp.total_matches, 0) ,2) AS total_goal_contributions_pg

FROM players pl
LEFT JOIN base_perf bp
ON pl.player_id = bp.player_id
