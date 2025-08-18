-- Build a superset of clubs referenced anywhere, and enrich with known details

WITH clubs_from_refs AS (
    SELECT home_club_id    AS club_id FROM {{ ref('stg_games') }}
    UNION
    SELECT away_club_id    AS club_id FROM {{ ref('stg_games') }}
    UNION
    SELECT club_id         AS club_id FROM {{ ref('stg_club_games') }}
    UNION
    SELECT opponent_id     AS club_id FROM {{ ref('stg_club_games') }}
    UNION
    SELECT club_id         AS club_id FROM {{ ref('stg_game_events') }}
    UNION
    SELECT club_id         AS club_id FROM {{ ref('stg_game_lineups') }}
    UNION
    SELECT current_club_id AS club_id FROM {{ ref('stg_players') }}
    UNION
    SELECT current_club_id AS club_id FROM {{ ref('stg_player_valuations') }}
    UNION
    SELECT from_club_id    AS club_id FROM {{ ref('stg_transfers') }}
    UNION
    SELECT to_club_id      AS club_id FROM {{ ref('stg_transfers') }}
    UNION
    SELECT player_club_id        AS club_id FROM {{ ref('stg_appearances') }}
    UNION
    SELECT player_current_club_id AS club_id FROM {{ ref('stg_appearances') }}
),
all_ids AS (
    SELECT DISTINCT club_id
    FROM clubs_from_refs
    WHERE club_id IS NOT NULL
)

SELECT
    ids.club_id,
    c.domestic_competition_id,
    c.name,
    c.total_market_value,
    c.net_transfer_record,
    c.squad_size,
    c.average_age,
    c.foreigners_number,
    c.foreigners_percentage,
    c.national_team_players,
    c.stadium_name,
    c.stadium_seats,
    c.coach_name,
    c.last_season
FROM all_ids ids
LEFT JOIN {{ ref('stg_clubs') }} c USING (club_id)
