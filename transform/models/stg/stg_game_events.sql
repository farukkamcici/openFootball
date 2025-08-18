WITH source AS (
    SELECT *
    FROM {{ source('tm', 'game_events') }}
    WHERE game_id IS NOT NULL
      AND club_id IS NOT NULL
      AND player_id IS NOT NULL
)

SELECT
    -- Primary key
    game_event_id,

    -- Foreign keys
    game_id,
    club_id,
    player_id,
    player_in_id,
    player_assist_id,

    -- Time info
    {{ to_date('date') }} AS date,
    {{ non_negative('minute') }} AS minute,

    -- Event info
    {{ clean_string('type') }} AS type,
    {{ clean_string('description') }} AS description

FROM source
