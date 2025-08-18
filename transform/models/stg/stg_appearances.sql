WITH source AS (
    SELECT *
    FROM {{ source('tm', 'appearances') }}
    WHERE appearance_id IS NOT NULL
      AND player_id IS NOT NULL
      AND game_id IS NOT NULL
      AND competition_id IS NOT NULL
)

SELECT
    -- ID columns
    appearance_id,
    game_id,
    player_id,

    -- Foreign keys
    competition_id,
    player_club_id,
    player_current_club_id,

    -- Player info
    {{ clean_string('player_name') }} AS player_name,
    {{ to_date('date') }} AS date,

    -- Match stats
    {{ non_negative('minutes_played') }} AS minutes_played,
    {{ non_negative('goals') }} AS goals,
    {{ non_negative('assists') }} AS assists,
    {{ non_negative('yellow_cards') }} AS yellow_cards,
    {{ non_negative('red_cards') }} AS red_cards

FROM source
