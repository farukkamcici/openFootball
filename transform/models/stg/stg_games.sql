WITH source AS (
    SELECT *
    FROM {{ source('tm', 'games') }}
    WHERE game_id IS NOT NULL
      AND home_club_id IS NOT NULL
      AND away_club_id IS NOT NULL
)

SELECT
    game_id,
    competition_id,
    season,
    round,
    {{ to_date('date') }} AS date,

    -- HOME CLUB
    home_club_id,
    {{ clean_string('home_club_name') }} AS home_club_name,
    {{ non_negative('home_club_goals') }} AS home_club_goals,
    {{ clean_string('home_club_formation') }} AS home_club_formation,
    {{ clean_string('home_club_manager_name') }} AS home_club_manager_name,
    {{ int_or_zero('home_club_position') }} AS home_club_position,

    -- AWAY CLUB
    away_club_id,
    {{ clean_string('away_club_name') }} AS away_club_name,
    {{ non_negative('away_club_goals') }} AS away_club_goals,
    {{ clean_string('away_club_formation') }} AS away_club_formation,
    {{ clean_string('away_club_manager_name') }} AS away_club_manager_name,
    {{ int_or_zero('away_club_position') }} AS away_club_position,

    -- MATCH INFO
    {{ clean_string('competition_type') }} AS competition_type,
    {{ clean_string('stadium') }} AS stadium,
    {{ clean_string('referee') }} AS referee,
    {{ int_or_zero('attendance') }} AS attendance

FROM source
