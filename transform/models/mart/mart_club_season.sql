{{ config(MATERIALIZED='TABLE') }}

WITH games_unioned AS (
    SELECT
        season,
        home_club_id AS club_id,
        home_club_goals AS goals_for,
        away_club_goals AS goals_against,
        home_points AS points,
        CASE WHEN home_points = 3 THEN 1 ELSE 0 END AS wins,
        CASE WHEN home_points = 1 THEN 1 ELSE 0 END AS draws,
        CASE WHEN home_points = 0 THEN 1 ELSE 0 END AS losses
    FROM {{ ref('mart_game_facts') }}

    UNION ALL

    SELECT
        season,
        away_club_id AS club_id,
        away_club_goals AS goals_for,
        home_club_goals AS goals_against,
        away_points AS points,
        CASE WHEN away_points = 3 THEN 1 ELSE 0 END AS wins,
        CASE WHEN away_points = 1 THEN 1 ELSE 0 END AS draws,
        CASE WHEN away_points = 0 THEN 1 ELSE 0 END AS losses
    FROM {{ ref('mart_game_facts') }}
),

club_games AS (
    SELECT
        season,
        club_id,
        COUNT(*) AS games_played,
        SUM(goals_for) AS goals_for,
        SUM(goals_against) AS goals_against,
        SUM(wins) AS wins,
        SUM(draws) AS draws,
        SUM(losses) AS losses,
        SUM(points) AS points,
        SUM(goals_for) - SUM(goals_against) AS goal_difference
    FROM games_unioned
    GROUP BY club_id, season
),

clubs_squad AS (
    SELECT
        g.season,
        a.player_club_id AS club_id,
        COUNT(DISTINCT a.player_id) AS squad_size,
        COALESCE(SUM(a.goals), 0) AS goals,
        COALESCE(SUM(a.assists), 0) AS assists,
        COALESCE(SUM(a.yellow_cards), 0) AS yellow_cards,
        COALESCE(SUM(a.red_cards), 0) AS red_cards
    FROM {{ ref('stg_appearances') }} AS a
    JOIN {{ ref('stg_games') }} AS g
      ON a.game_id = g.game_id
    GROUP BY g.season, a.player_club_id
)

SELECT
    g.season,
    g.club_id,
    c.name,
    g.games_played,
    g.wins,
    g.draws,
    g.losses,
    g.points,
    g.goals_for,
    g.goals_against,
    g.goal_difference,
    COALESCE(s.squad_size, 0) AS squad_size,
    COALESCE(s.goals, 0) AS squad_goals,
    COALESCE(s.assists, 0) AS squad_assists,
    COALESCE(s.yellow_cards, 0) AS squad_yellow_cards,
    COALESCE(s.red_cards, 0) AS squad_red_cards
FROM club_games AS g
LEFT JOIN clubs_squad AS s
ON g.club_id = s.club_id
AND g.season  = s.season
INNER JOIN {{ ref('stg_clubs') }} c
ON g.club_id = c.club_id
