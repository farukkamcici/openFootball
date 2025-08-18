WITH src AS (
    SELECT * FROM {{ source('tm', 'competitions') }}
)

SELECT
    CAST(competition_id AS varchar)         AS competition_id,
    NULLIF(TRIM(competition_code), '')      AS competition_code,
    nullif(trim(name), '')                  as competition_name,
    nullif(trim(type), '')                  as competition_type,
    nullif(trim(sub_type), '')              as competition_sub_type,
    cast(country_id as bigint)              as country_id,
    nullif(trim(country_name), '')          as country_name,
    COALESCE(is_major_national_league, FALSE) AS is_top_5
from src
