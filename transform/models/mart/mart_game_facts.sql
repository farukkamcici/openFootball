{{ config(materialized='table') }}

WITH src AS (
SELECT g.game_id,
    g.competition_id,
    g.season,
    g.date,
    g.home_club_id,
    g.away_club_id,
    g.home_club_goals,
    g.away_club_goals
FROM {{ ref('stg_games') }} g
INNER JOIN {{ ref('stg_clubs') }} c ON g.home_club_id = c.club_id
INNER JOIN {{ ref('stg_competitions') }} co ON g.competition_id = co.competition_id
)

, facts AS (
    SELECT
            game_id,
            competition_id,
            season,
            date,
            home_club_id,
            away_club_id,
            home_club_goals,
            away_club_goals,
            (home_club_goals - away_club_goals) AS goals_difference,
            CASE
                WHEN (home_club_goals - away_club_goals) > 0 THEN 'home_win'
                WHEN (home_club_goals - away_club_goals) < 0 THEN 'away_win'
                ELSE 'draw'
            END AS result
    FROM src
)

, points AS (
    SELECT
        game_id,
        CASE
            WHEN result = 'home_win' THEN 3
            WHEN result = 'draw' THEN 1
            ELSE 0
        END AS home_points,
        CASE
            WHEN result = 'away_win' THEN 3
            WHEN result = 'draw' THEN 1
            ELSE 0
        END AS away_points
    FROM facts
)

SELECT
    f.*,
    p.home_points,
    p.away_points
FROM facts f
LEFT JOIN points p ON f.game_id = p.game_id
