{{ config(materialized='table') }}

WITH transfers AS (
    SELECT
        t.player_id,
        t.transfer_date,
        t.transfer_fee,
        p.date_of_birth,
        DATE_DIFF('year', p.date_of_birth, t.transfer_date) AS age_at_transfer
    FROM {{ ref('stg_transfers') }} t
    JOIN {{ ref('stg_players') }} p
      ON t.player_id = p.player_id
    WHERE t.transfer_fee IS NOT NULL
),

bucketed AS (
    SELECT
        CASE
            WHEN age_at_transfer BETWEEN 15 AND 19 THEN '15-19'
            WHEN age_at_transfer BETWEEN 20 AND 24 THEN '20-24'
            WHEN age_at_transfer BETWEEN 25 AND 29 THEN '25-29'
            WHEN age_at_transfer BETWEEN 30 AND 34 THEN '30-34'
            ELSE '35+'
        END AS age_bucket,
        transfer_fee
    FROM transfers
    WHERE age_at_transfer IS NOT NULL
)

SELECT
    age_bucket,
    COUNT(*) AS transfer_count,
    ROUND(AVG(transfer_fee), 2) AS avg_transfer_fee
FROM bucketed
GROUP BY age_bucket
ORDER BY age_bucket
