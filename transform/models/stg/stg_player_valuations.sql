WITH source AS (
    SELECT *
    FROM {{ source('tm', 'player_valuations') }}
    WHERE player_id IS NOT NULL
      AND current_club_id IS NOT NULL
      AND player_club_domestic_competition_id IS NOT NULL
)


SELECT
    -- Composite key
    player_id,
    {{ to_date('date') }} AS date,

    -- Value info
    {{ int_or_null('market_value_in_eur') }} AS market_value_in_eur,

    -- Club context
    current_club_id,
    player_club_domestic_competition_id

FROM source
