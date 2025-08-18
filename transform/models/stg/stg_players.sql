WITH source AS (
    SELECT *
    FROM {{ source('tm', 'players') }}
    WHERE player_id IS NOT NULL
      AND current_club_id IS NOT NULL
)

SELECT
    -- Identity
    player_id,
    {{ clean_string('first_name') }} AS first_name,
    {{ clean_string('last_name') }} AS last_name,
    {{ clean_string('name') }} AS name,

    -- Club context
    current_club_id,
    current_club_domestic_competition_id,
    {{ int_or_null('last_season') }} AS last_season,

    -- Location / Birth
    {{ clean_string('country_of_birth') }} AS country_of_birth,
    {{ clean_string('city_of_birth') }} AS city_of_birth,
    {{ clean_string('country_of_citizenship') }} AS country_of_citizenship,
    {{ to_date('date_of_birth') }} AS date_of_birth,

    -- Physical & tactical attributes
    {{ clean_string('position') }} AS position,
    {{ clean_string('sub_position') }} AS sub_position,
    {{ clean_string('foot') }} AS foot,
    {{ int_or_null('height_in_cm') }} AS height_in_cm,

    -- Contract info
    {{ to_date('contract_expiration_date') }} AS contract_expiration_date,
    {{ clean_string('agent_name') }} AS agent_name,

    -- Market values
    {{ bigint_or_null('market_value_in_eur') }} AS market_value_in_eur,
    {{ bigint_or_null('highest_market_value_in_eur') }} AS highest_market_value_in_eur

FROM source
