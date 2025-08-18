WITH source AS (
    SELECT *
    FROM {{ source('tm', 'transfers') }}
    WHERE player_id IS NOT NULL
      AND from_club_id IS NOT NULL
      AND to_club_id IS NOT NULL
)

SELECT
    -- Player and time
    player_id,
    {{ clean_string('player_name') }} AS player_name,
    {{ to_date('transfer_date') }} AS transfer_date,
    {{ int_or_null('transfer_season') }} AS transfer_season,

    -- Clubs
    from_club_id,
    {{ clean_string('from_club_name') }} AS from_club_name,
    to_club_id,
    {{ clean_string('to_club_name') }} AS to_club_name,

    -- Values
    {{ decimal_or_null('transfer_fee') }} AS transfer_fee,
    {{ decimal_or_null('market_value_in_eur') }} AS market_value_in_eur

FROM source
