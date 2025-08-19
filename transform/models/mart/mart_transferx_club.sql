{{ config(materialized='table') }}

-- base transfer-level table
WITH base AS (
    SELECT
        m.player_id,
        m.season,
        m.from_club_id,
        m.to_club_id,
        m.transfer_category,
        m.fee_norm
    FROM {{ ref('mart_transferx_player') }} m
),

-- incoming side (to_club_id)
incoming AS (
    SELECT
        b.to_club_id AS club_id,
        b.season,
        COUNT(*) AS incoming_total,
        SUM(b.fee_norm) AS transfer_spend,
        SUM(CASE WHEN b.transfer_category = 'free' THEN 1 ELSE 0 END)           AS incoming_free_cnt,
        SUM(CASE WHEN b.transfer_category = 'paid_transfer' THEN 1 ELSE 0 END) AS incoming_paid_cnt,
        SUM(CASE WHEN b.transfer_category = 'loan_out' THEN 1 ELSE 0 END)   AS incoming_loan_cnt,
        SUM(CASE WHEN b.transfer_category = 'loan_return' THEN 1 ELSE 0 END) AS incoming_loan_return_cnt
    FROM base b
    WHERE b.to_club_id IS NOT NULL
    GROUP BY 1,2
),

-- outgoing side (from_club_id)
outgoing AS (
    SELECT
        b.from_club_id AS club_id,
        b.season,
        COUNT(*) AS outgoing_total,
        SUM(b.fee_norm) AS transfer_income,
        SUM(CASE WHEN b.transfer_category = 'free' THEN 1 ELSE 0 END)           AS outgoing_free_cnt,
        SUM(CASE WHEN b.transfer_category = 'paid_transfer' THEN 1 ELSE 0 END) AS outgoing_paid_cnt,
        SUM(CASE WHEN b.transfer_category = 'loan_out' THEN 1 ELSE 0 END)   AS outgoing_loan_cnt,
        SUM(CASE WHEN b.transfer_category = 'loan_return' THEN 1 ELSE 0 END) AS outgoing_loan_return_cnt
    FROM base b
    WHERE b.from_club_id IS NOT NULL
    GROUP BY 1,2
),

-- merge incoming and outgoing
merged AS (
    SELECT
        COALESCE(i.club_id, o.club_id) AS club_id,
        COALESCE(i.season,  o.season)  AS season,

        COALESCE(i.incoming_total, 0)  AS incoming_total,
        COALESCE(o.outgoing_total, 0)  AS outgoing_total,

        COALESCE(i.incoming_free_cnt, 0)          AS incoming_free_cnt,
        COALESCE(i.incoming_paid_cnt, 0)          AS incoming_paid_cnt,
        COALESCE(i.incoming_loan_cnt, 0)         AS incoming_loan_cnt,
        COALESCE(i.incoming_loan_return_cnt, 0)  AS incoming_loan_return_cnt,

        COALESCE(o.outgoing_free_cnt, 0)          AS outgoing_free_cnt,
        COALESCE(o.outgoing_paid_cnt, 0)          AS outgoing_paid_cnt,
        COALESCE(o.outgoing_loan_cnt, 0)         AS outgoing_loan_cnt,
        COALESCE(o.outgoing_loan_return_cnt, 0)  AS outgoing_loan_return_cnt,

        COALESCE(i.transfer_spend, 0)  AS transfer_spend,
        COALESCE(o.transfer_income, 0) AS transfer_income
    FROM incoming i
    FULL OUTER JOIN outgoing o
      ON i.club_id = o.club_id AND i.season = o.season
),

-- attach club names
with_name AS (
    SELECT
        m.*,
        c.name AS club_name
    FROM merged m
    INNER JOIN {{ ref('stg_clubs') }} c
      ON m.club_id = c.club_id
)

-- final club-season summary
SELECT
    club_id,
    club_name,
    season,

    incoming_total,
    outgoing_total,

    incoming_free_cnt,
    incoming_paid_cnt,
    incoming_loan_cnt,
    incoming_loan_return_cnt,

    outgoing_free_cnt,
    outgoing_paid_cnt,
    outgoing_loan_cnt,
    outgoing_loan_return_cnt,

    transfer_spend,
    transfer_income,
    transfer_spend - transfer_income AS net_spend,

    CASE WHEN incoming_total > 0 THEN ROUND(incoming_free_cnt * 1.0 / incoming_total, 1) END AS incoming_free_rate,
    CASE WHEN incoming_total > 0 THEN ROUND(incoming_paid_cnt * 1.0 / incoming_total, 1) END AS incoming_paid_rate,
    CASE WHEN outgoing_total > 0 THEN ROUND(outgoing_paid_cnt * 1.0 / outgoing_total, 1) END AS outgoing_paid_rate
FROM with_name
