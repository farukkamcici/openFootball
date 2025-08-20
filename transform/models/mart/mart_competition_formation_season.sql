{{ config(materialized='table') }}

WITH games_unioned AS (
    SELECT
        game_id,
        competition_id,
        season,
        home_club_formation AS club_formation,
        home_club_position AS club_position,
        home_club_goals AS goals_for,
        away_club_goals AS goals_against,
        CASE
            WHEN home_club_goals > away_club_goals THEN 3
            WHEN home_club_goals < away_club_goals THEN 0
            ELSE 1
        END AS points,
        CASE
            WHEN home_club_goals > away_club_goals THEN 'win'
            WHEN home_club_goals = away_club_goals THEN 'draw'
            WHEN home_club_goals < away_club_goals THEN 'loss'
        END AS result,
    FROM {{ ref('stg_games') }}
    WHERE home_club_formation IS NOT NULL

    UNION ALL

        SELECT
        game_id,
        competition_id,
        season,
        away_club_formation AS club_formation,
        away_club_position AS club_position,
        away_club_goals AS goals_for,
        home_club_goals AS goals_against,
        CASE
            WHEN home_club_goals < away_club_goals THEN 3
            WHEN home_club_goals > away_club_goals THEN 0
            ELSE 1
        END AS points,
        CASE
            WHEN home_club_goals < away_club_goals THEN 'win'
            WHEN home_club_goals = away_club_goals THEN 'draw'
            WHEN home_club_goals > away_club_goals THEN 'loss'
        END AS result,
    FROM {{ ref('stg_games') }}
    WHERE away_club_formation IS NOT NULL
)

, agg AS (
    SELECT
        competition_id,
        season,
        club_formation,
        COUNT(*) AS games_played,
        SUM(goals_for) AS goals_for,
        SUM(goals_against) AS goals_against,
        ROUND(AVG(goals_for), 2) AS avg_goals_for,
        ROUND(AVG(goals_against), 2) AS avg_goals_against,
        ROUND(AVG(points), 2) AS ppg,
        ROUND(AVG(club_position), 2) AS avg_position,
        SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws,
        SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
        ROUND((SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0)) * 100, 1) AS win_percentage
    FROM games_unioned
    GROUP BY competition_id, season, club_formation
)

SELECT
    {{ title_case ('co.competition_name') }} as competition_name,
    a.*
FROM agg a
INNER JOIN {{ ref('stg_competitions') }} co
ON a.competition_id = co.competition_id
