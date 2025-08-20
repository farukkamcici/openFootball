# Mart Models: Reference

Overview of every `mart_*` model, including grain, purpose, and notable fields. These marts build on `stg_*` sources, are materialized as tables/views, and are tested via `mart_schema.yml`. Run with `make dbt`.

## mart_game_facts
- Grain: game-level (`game_id`).
- Purpose: Canonical game facts with result and points.
- Notable: `competition_id`, `season`, `date`, `home_club_id`, `away_club_id`, `home_club_goals`, `away_club_goals`, `goals_difference`, `result`, `home_points`, `away_points`.

## mart_club_season
- Grain: club-season (`season`, `club_id`).
- Purpose: Club seasonal summary across all competitions.
- Notable: `name`, `games_played`, `wins`, `draws`, `losses`, `points`, `goals_for`, `goals_against`, `goal_difference`, squad: `squad_size`, `squad_goals`, `squad_assists`, `squad_yellow_cards`, `squad_red_cards`.

## mart_competition_club_season
- Grain: competition-club-season (`season`, `competition_id`, `club_id`).
- Purpose: Club seasonal summary within a competition.
- Notable: `club_name`, `competition_name`, `games_played`, `wins`, `draws`, `losses`, `points`, `goals_for`, `goals_against`, `goal_difference`, squad breakdowns.

## mart_club_season_europe
- Grain: competition-club-season (filtered to European comps).
- Purpose: Subset of `mart_competition_club_season` for `CL`, `EL`, `UCOL`.
- Notable: Same columns as `mart_competition_club_season`.

## mart_player_season
- Grain: player-season (`player_id`, `season`).
- Purpose: Player seasonal performance across all competitions.
- Notable: `player_name`, `games_played`, `minutes_played`, `goals`, `assists`, `total_goals_and_assists`, cards, `has_600_minutes`, per90: `goals_per90`, `assists_per90`, `goal_plus_assist_per90`, `efficiency_score`, `season_last_value_eur`.

## mart_competition_player_season
- Grain: competition-player-season (`player_id`, `season`, `competition_id`).
- Purpose: Player seasonal performance within a competition.
- Notable: `player_name`, `competition_name`, `games_played`, `minutes_played`, `goals`, `assists`, `total_goals_and_assists`, cards, `has_180_minutes`, per90 metrics, `efficiency_score`, `season_last_value_eur`.

## mart_player_season_europe
- Grain: competition-player-season (filtered to European comps).
- Purpose: Subset of `mart_competition_player_season` for `CL`, `EL`, `UCOL`.
- Notable: Same columns as `mart_competition_player_season`.

## mart_player_valuation_season
- Grain: player-season (`player_id`, `season`).
- Purpose: Player market value deltas within July–June seasons.
- Notable: `name`, `first_market_value`, `last_market_value`, `min_market_value`, `max_market_value`, `value_change_amount`, `value_change_percentage`.

## mart_player_career_summary
- Grain: player (`player_id`).
- Purpose: Career totals merged with player metadata.
- Notable: `player_name`, `date_of_birth`, `country_of_citizenship`, `foot`, `position`, `sub_position`, `career_peak_value_eur`, `last_season`, totals: `total_matches`, `total_minutes`, `total_goals`, `total_assists`, `total_goal_contributions`, cards, per-game: `gpg`, `apg`, `total_goal_contributions_pg`.

## mart_player_value_performance_corr
- Grain: player-season (`player_id`, `season`).
- Purpose: Join of performance and valuation to analyze age/value/performance relationships.
- Notable: `player_name`, `age_in_season`, `minutes_played`, per90 metrics, `efficiency_score`, `first_market_value`, `last_market_value`, `value_change_amount`, `value_change_percentage`.

## mart_club_formation_season
- Grain: competition-club-formation-season (`competition_id`, `season`, `club_id`, `club_formation`).
- Purpose: Club performance by season and formation.
- Notable: `club_name`, `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `wins`, `draws`, `losses`, `win_percentage`, `competition_name`.

## mart_competition_formation_season
- Grain: competition-formation-season (`competition_id`, `season`, `club_formation`).
- Purpose: Formation performance by competition and season.
- Notable: `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `wins`, `draws`, `losses`, `win_percentage`, `competition_name`.

## mart_formation_history_performance
- Grain: formation (`club_formation`).
- Purpose: Global formation performance across all games.
- Notable: `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `wins`, `draws`, `losses`, `win_percentage`.

## mart_manager_performance
- Grain: manager (`manager_name`).
- Purpose: Manager performance summary from club games.
- Notable: `games_played`, `wins`, `draws`, `losses`, `points`, `ppg`, `win_rate`.

## mart_manager_formation_performance
- Grain: manager-formation (`manager_name`, `club_formation`).
- Purpose: Manager performance by chosen formation.
- Notable: `games_played`, `avg_goals_for`, `avg_goals_against`, `wins`, `draws`, `losses`, `points`, `ppg`, `win_rate`.

## mart_transfer_player
- Grain: player-transfer date (`player_id`, `transfer_date`).
- Purpose: Player transfer records with categories and normalized fees.
- Notable: `season`, `from_club_id`, `from_club_name`, `to_club_id`, `to_club_name`, `market_value_in_eur`, `transfer_fee`, flags: `is_loan_out`, `is_loan_return`, `is_free_transfer`, `is_retired_or_without_club`, derived `transfer_category`, `fee_norm`.

## mart_transfer_club
- Grain: club-season (`club_id`, `season`).
- Purpose: Club transfer activity summary (incoming/outgoing, spend/income, rates).
- Notable: `club_name`, counts: `incoming_total`, `outgoing_total`, free/paid/loan breakdowns, finances: `transfer_spend`, `transfer_income`, `net_spend`, rates: `incoming_free_rate`, `incoming_paid_rate`, `outgoing_paid_rate`.

## mart_transfer_age_fee_profile
- Grain: age bucket (`age_bucket`).
- Purpose: Distribution of transfer fees by player age at transfer.
- Notable: `transfer_count`, `avg_transfer_fee`.

---

Notes
- All names are generally Title Cased via macros where present.
- See `mart_schema.yml` for tests/constraints and column-level checks.
- European subsets filter competitions: `CL`, `EL`, `UCOL`.
