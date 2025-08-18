WITH source AS (
    SELECT *
    FROM {{ source('tm', 'clubs') }}
    WHERE club_id IS NOT NULL
)

SELECT
    -- Primary key
    club_id,

    -- Foreign key
    domestic_competition_id,

    -- Club identity
    {{ clean_string('name') }} AS name,

    -- Market value and transfer
    {{ decimal_or_null('total_market_value') }} AS total_market_value,
    {{ decimal_or_null('net_transfer_record') }} AS net_transfer_record,

    -- Squad stats
    {{ int_or_null('squad_size') }} AS squad_size,
    {{ decimal_or_null('average_age', 5, 2) }} AS average_age,
    {{ int_or_null('foreigners_number') }} AS foreigners_number,
    {{ decimal_or_null('foreigners_percentage', 5, 2) }} AS foreigners_percentage,
    {{ int_or_null('national_team_players') }} AS national_team_players,

    -- Stadium info
    {{ clean_string('stadium_name') }} AS stadium_name,
    {{ int_or_null('stadium_seats') }} AS stadium_seats,

    -- Other
    {{ clean_string('coach_name') }} AS coach_name,
    {{ int_or_null('last_season') }} AS last_season

FROM source
