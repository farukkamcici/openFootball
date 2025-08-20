{{ config(materialized='table') }}
WITH base AS (
    SELECT
        game_id,
        own_manager_name AS manager_name,
        own_goals,
        opponent_goals,
        is_win
    FROM {{ ref('stg_club_games') }}
    WHERE own_manager_name IS NOT NULL
),

scored AS (
    SELECT
        manager_name,
        1 AS game_cnt,
        CASE WHEN is_win = TRUE THEN 1 ELSE 0 END AS win_cnt,
        CASE WHEN is_win = FALSE AND own_goals = opponent_goals THEN 1 ELSE 0 END AS draw_cnt,
        CASE WHEN is_win = FALSE AND own_goals <> opponent_goals THEN 1 ELSE 0 END AS loss_cnt,
        CASE
            WHEN is_win = TRUE THEN 3
            WHEN is_win = FALSE AND own_goals = opponent_goals THEN 1
            ELSE 0
        END AS points_cnt
    FROM base
),

agg AS (
    SELECT
        manager_name,
        SUM(game_cnt) AS games_played,
        SUM(win_cnt) AS wins,
        SUM(draw_cnt) AS draws,
        SUM(loss_cnt) AS losses,
        SUM(points_cnt) AS points
    FROM scored
    GROUP BY manager_name
)

SELECT
    manager_name,
    games_played,
    wins,
    draws,
    losses,
    points,
    ROUND(points * 1.0 / NULLIF(games_played, 0), 2) AS ppg,
    ROUND(wins * 1.0 / NULLIF(games_played, 0), 2)  AS win_rate
FROM agg
