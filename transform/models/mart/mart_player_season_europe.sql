{{ config(MATERIALIZED='view') }}

SELECT
    *
FROM {{ ref('mart_competition_player_season') }}
WHERE competition_id = 'CL'
OR competition_id = 'EL'
OR competition_id = 'UCOL'
