{{ config(materialized='table') }}

-- source transfers
WITH src AS (
    SELECT
        t.player_id,
        t.player_name,
        t.transfer_date,
        t.from_club_id,
        t.from_club_name,
        t.to_club_id,
        t.to_club_name,
        t.market_value_in_eur,
        COALESCE(t.transfer_fee, 0) AS transfer_fee_raw
    FROM {{ ref('stg_transfers') }} t
),

-- assign season (July → June)
seasoned AS (
    SELECT
        s.*,
        CASE
          WHEN EXTRACT(MONTH FROM s.transfer_date) >= 7
            THEN CONCAT(EXTRACT(YEAR FROM s.transfer_date), '/', EXTRACT(YEAR FROM s.transfer_date) + 1)
          ELSE CONCAT(EXTRACT(YEAR FROM s.transfer_date) - 1, '/', EXTRACT(YEAR FROM s.transfer_date))
        END AS season
    FROM src s
),

-- retired/without club + free (zero fee)
flags AS (
    SELECT
        x.*,
        (x.to_club_name IN ('Retired','Without Club') OR x.from_club_name IN ('Retired','Without Club')) AS is_retired_or_without_club,
        (x.transfer_fee_raw = 0) AS is_free_transfer
    FROM seasoned x
),

-- order transfers per player
ordered AS (
    SELECT
        f.*,
        ROW_NUMBER() OVER (PARTITION BY f.player_id ORDER BY f.transfer_date) AS rn
    FROM flags f
),

-- detect loan cycles: A->B (0) then B->A (0), within <= 24 months
pairs AS (
    SELECT
        o1.player_id,
        o1.rn AS rn_out,
        o2.rn AS rn_ret
    FROM ordered o1
    JOIN ordered o2
      ON o1.player_id = o2.player_id
     AND o2.rn = o1.rn + 1
    WHERE o1.transfer_fee_raw = 0
      AND o2.transfer_fee_raw = 0
      AND o1.from_club_id = o2.to_club_id
      AND o1.to_club_id   = o2.from_club_id
      AND DATE_DIFF('month', o1.transfer_date, o2.transfer_date) <= 24
),

loan_flags AS (
    SELECT player_id, rn_out AS rn, 'loan_out' AS loan_tag FROM pairs
    UNION ALL
    SELECT player_id, rn_ret AS rn, 'loan_return' AS loan_tag FROM pairs
)

-- final transfer table
SELECT
    o.player_id,
    o.player_name,
    o.transfer_date,
    o.season,
    o.from_club_id,
    o.from_club_name,
    o.to_club_id,
    o.to_club_name,
    o.market_value_in_eur,
    o.transfer_fee_raw AS transfer_fee,

    -- loan flags (always boolean)
    COALESCE(BOOL_OR(lf.loan_tag = 'loan_out'),    FALSE) AS is_loan_out,
    COALESCE(BOOL_OR(lf.loan_tag = 'loan_return'), FALSE) AS is_loan_return,

    -- other flags (always boolean)
    COALESCE(o.is_free_transfer,           FALSE) AS is_free_transfer,
    COALESCE(o.is_retired_or_without_club, FALSE) AS is_retired_or_without_club,

    -- transfer category (priority order)
    CASE
      WHEN COALESCE(BOOL_OR(lf.loan_tag='loan_out'),    FALSE) THEN 'loan_out'
      WHEN COALESCE(BOOL_OR(lf.loan_tag='loan_return'), FALSE) THEN 'loan_return'
      WHEN COALESCE(o.is_free_transfer, FALSE) THEN 'free'
      WHEN COALESCE(o.is_retired_or_without_club, FALSE) THEN 'retired_or_without_club'
      WHEN o.transfer_fee_raw > 0 THEN 'paid_transfer'
      ELSE 'other'
    END AS transfer_category,

    -- normalized fee: if NULL/0 → 0, else raw value
    CASE
      WHEN o.transfer_fee_raw IS NULL OR o.transfer_fee_raw = 0 THEN 0
      ELSE o.transfer_fee_raw
    END AS fee_norm

FROM ordered o
LEFT JOIN loan_flags lf
  ON o.player_id = lf.player_id AND o.rn = lf.rn
GROUP BY
    o.player_id, o.player_name, o.transfer_date, o.season,
    o.from_club_id, o.from_club_name, o.to_club_id, o.to_club_name,
    o.market_value_in_eur, o.transfer_fee_raw,
    o.is_free_transfer, o.is_retired_or_without_club
