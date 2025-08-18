WITH source AS (
    SELECT *
    FROM {{ source('tm', 'club_games') }}
    WHERE game_id IS NOT NULL
      AND club_id IS NOT NULL
      AND opponent_id IS NOT NULL
)

SELECT
    -- Composite key
    game_id,
    club_id,

    -- Opponent reference
    opponent_id,

    -- Club info
    {{ non_negative('own_goals') }} AS own_goals,
    {{ int_or_zero('own_position') }} AS own_position,
    {{ clean_string('own_manager_name') }} AS own_manager_name,

    -- Opponent info
    {{ non_negative('opponent_goals') }} AS opponent_goals,
    {{ int_or_zero('opponent_position') }} AS opponent_position,
    {{ clean_string('opponent_manager_name') }} AS opponent_manager_name,

    -- Match flags
    {{ clean_string('hosting') }} AS hosting,
    {{ int_or_null('is_win') }} AS is_win

FROM source
