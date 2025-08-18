WITH source AS (
    SELECT *
    FROM {{ source('tm', 'game_lineups') }}
    WHERE game_id IS NOT NULL
      AND club_id IS NOT NULL
      AND player_id IS NOT NULL
)
SELECT
    -- Composite key (practical PK)
    game_id,
    club_id,
    player_id,

    -- Info
    {{ clean_string('player_name') }} AS player_name,
    {{ clean_string('position') }} AS position,
    {{ clean_string('type') }} AS type,
    {{ int_or_null('number') }} AS number,
    {{ int_or_zero('team_captain') }} AS team_captain,

    -- Date of lineup
    {{ to_date('date') }} AS date

FROM source
