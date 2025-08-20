{{ config(materialized='table') }}
WITH home_side AS (
    SELECT
        g.home_club_manager_name AS manager_name,
        g.home_club_formation   AS club_formation,
        g.home_club_goals       AS goals_for,
        g.away_club_goals       AS goals_against
    FROM {{ ref('stg_games') }} AS g
    WHERE g.home_club_manager_name IS NOT NULL
      AND g.home_club_formation IS NOT NULL
),
away_side AS (
    SELECT
        g.away_club_manager_name AS manager_name,
        g.away_club_formation    AS club_formation,
        g.away_club_goals        AS goals_for,
        g.home_club_goals        AS goals_against
    FROM {{ ref('stg_games') }} AS g
    WHERE g.away_club_manager_name IS NOT NULL
      AND g.away_club_formation IS NOT NULL
),
stacked AS (
    SELECT * FROM home_side
    UNION ALL
    SELECT * FROM away_side
),
scored AS (
    SELECT
        manager_name,
        club_formation,
        goals_for,
        goals_against,
        1 AS game_cnt,
        CASE WHEN goals_for > goals_against THEN 1 ELSE 0 END AS win_cnt,
        CASE WHEN goals_for = goals_against THEN 1 ELSE 0 END AS draw_cnt,
        CASE WHEN goals_for < goals_against THEN 1 ELSE 0 END AS loss_cnt,
        CASE
            WHEN goals_for > goals_against THEN 3
            WHEN goals_for = goals_against THEN 1
            ELSE 0
        END AS points_cnt
    FROM stacked
)
SELECT
    manager_name,
    club_formation,
    SUM(game_cnt)  AS games_played,
    ROUND(AVG(goals_for), 2) AS avg_goals_for,
    ROUND(AVG(goals_against), 2) AS avg_goals_against,
    SUM(win_cnt)   AS wins,
    SUM(draw_cnt)  AS draws,
    SUM(loss_cnt)  AS losses,
    SUM(points_cnt) AS points,
    ROUND(SUM(points_cnt) * 1.0 / NULLIF(SUM(game_cnt), 0), 2) AS ppg,
    ROUND(SUM(win_cnt)    * 1.0 / NULLIF(SUM(game_cnt), 0), 2) AS win_rate
FROM scored
GROUP BY manager_name, club_formation
