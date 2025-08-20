# Mart Models: Reference

Concise descriptions of each `mart_*` table and its key fields.

## mart_club_formation_season
- Purpose: Club performance by season and formation.
- Keys: Composite (`competition_id`, `season`, `club_id`, `club_formation`).
- Columns: `club_name`, `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `avg_position`, `wins`, `draws`, `losses`, `win_percentage`, `competition_name`.

## mart_club_season
- Purpose: Club seasonal summary across all competitions.
- Keys: Composite (`season`, `club_id`).
- Columns: `name`, `games_played`, `wins`, `draws`, `losses`, `points`, `goals_for`, `goals_against`, `goal_difference`, squad totals: `squad_size`, `squad_goals`, `squad_assists`, `squad_yellow_cards`, `squad_red_cards`.

## mart_competition_club_season
- Purpose: Club seasonal summary within a competition.
- Keys: Composite (`season`, `competition_id`, `club_id`).
- Columns: `club_name`, `competition_name`, `games_played`, `wins`, `draws`, `losses`, `points`, `goals_for`, `goals_against`, `goal_difference`, squad totals as above.

## mart_competition_formation_season
- Purpose: Formation performance by competition and season.
- Keys: Composite (`competition_id`, `season`, `club_formation`).
- Columns: `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `avg_position`, `wins`, `draws`, `losses`, `win_percentage`, `competition_name`.

## mart_competition_player_season
- Purpose: Player seasonal performance within a competition.
- Keys: Composite (`player_id`, `season`, `competition_id`).
- Columns: `player_name`, `competition_name`, `games_played`, `minutes_played`, `goals`, `assists`, `total_goals_and_assists`, cards, `has_180_minutes`, per90: `goals_per90`, `assists_per90`, `goal_plus_assist_per90`, `efficiency_score`, `season_last_value_eur`.

## mart_europe_club_season
- Purpose: European competitions subset of club-season (CL/EL/UCOL).
- Keys: Same as `mart_competition_club_season`.
- Columns: Same as `mart_competition_club_season` (filtered).

## mart_europe_player_season
- Purpose: European competitions subset of player-season (CL/EL/UCOL).
- Keys: Same as `mart_competition_player_season`.
- Columns: Same as `mart_competition_player_season` (filtered).

## mart_formation_performance_history
- Purpose: Formation performance across all games (global history).
- Key: `club_formation`.
- Columns: `games_played`, `goals_for`, `goals_against`, `avg_goals_for`, `avg_goals_against`, `ppg`, `avg_position`, `wins`, `draws`, `losses`, `win_percentage`.

## mart_game_facts
- Purpose: Game-level facts and derived points.
- Key: `game_id`.
- Columns: `competition_id`, `season`, `date`, `home_club_id`, `away_club_id`, `home_club_goals`, `away_club_goals`, `goals_difference`, `result`, `home_points`, `away_points`.

## mart_manager_performance
- Purpose: Manager performance summary.
- Note: Placeholder model (definition pending).

## mart_player_career_summary
- Purpose: Player career totals merged with metadata.
- Key: `player_id`.
- Columns: `player_name`, `date_of_birth`, `country_of_citizenship`, `foot`, `position`, `sub_position`, `career_peak_value_eur`, `last_season`, totals: `total_matches`, `total_minutes`, `total_goals`, `total_assists`, `total_goal_contributions`, cards, per-game: `gpg`, `apg`, `total_goal_contributions_pg`.

## mart_player_season
- Purpose: Player seasonal performance across all competitions.
- Keys: Composite (`player_id`, `season`).
- Columns: `player_name`, `games_played`, `minutes_played`, `goals`, `assists`, `total_goals_and_assists`, cards, `has_600_minutes`, per90 metrics, `efficiency_score`, `season_last_value_eur`.

## mart_player_valuation_season
- Purpose: Player market value deltas per season.
- Keys: Composite (`player_id`, `season`).
- Columns: `name`, `first_market_value`, `last_market_value`, `min_market_value`, `max_market_value`, `value_change_amount`, `value_change_percentage`.

## mart_transferx_club
- Purpose: Club transfer activity summary per season.
- Keys: Composite (`club_id`, `season`).
- Columns: `club_name`, counts: `incoming_total`, `outgoing_total`, free/paid/loan breakdowns, finances: `transfer_spend`, `transfer_income`, `net_spend`, rates: `incoming_free_rate`, `incoming_paid_rate`, `outgoing_paid_rate`.

## mart_transferx_player
- Purpose: Player transfer records with categories and fees.
- Keys: Composite (`player_id`, `transfer_date`).
- Columns: `player_name`, `season`, `from_club_id`, `from_club_name`, `to_club_id`, `to_club_name`, `market_value_in_eur`, `transfer_fee`, flags: `is_loan_out`, `is_loan_return`, `is_free_transfer`, `is_retired_or_without_club`, `transfer_category`, `fee_norm`.
