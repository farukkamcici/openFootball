# Stage Models: Reference

Concise descriptions of each `stg_*` table and its key fields.

## stg_appearances
- Purpose: Player match appearances and basic stats.
- Keys: `appearance_id` (PK); refs `game_id`, `player_id`, `competition_id`.
- Columns: `player_name`, `date`, `minutes_played`, `goals`, `assists`, `yellow_cards`, `red_cards`, `player_club_id`, `player_current_club_id`.

## stg_club_games
- Purpose: Club-centric view of a game vs opponent.
- Keys: Composite (`game_id`, `club_id`); ref `opponent_id`.
- Columns: Own side `own_goals`, `own_position`, `own_manager_name`; opponent side `opponent_goals`, `opponent_position`, `opponent_manager_name`; flags `hosting`, `is_win`.

## stg_clubs
- Purpose: Club attributes, squad and market info.
- Key: `club_id`; ref `domestic_competition_id`.
- Columns: `name`, `total_market_value`, `net_transfer_record`, `squad_size`, `average_age`, `foreigners_number`, `foreigners_percentage`, `national_team_players`, `stadium_name`, `stadium_seats`, `coach_name`, `last_season`.

## stg_competitions
- Purpose: Competition directory.
- Key: `competition_id`.
- Columns: `competition_code`, `competition_name`, `competition_type`, `competition_sub_type`, `country_id`, `country_name`, `is_top_5`.

## stg_game_events
- Purpose: In-game events (goals, cards, subs).
- Key: `game_event_id`; refs `game_id`, `club_id`, `player_id`, `player_in_id`, `player_assist_id`.
- Columns: `date`, `minute`, `type`, `description`.

## stg_game_lineups
- Purpose: Starting lineups and benches per game/club/player.
- Keys: Composite (`game_id`, `club_id`, `player_id`).
- Columns: `player_name`, `position`, `type`, `number`, `team_captain`, `date`.

## stg_games
- Purpose: Match-level record with teams and context.
- Key: `game_id`; refs `competition_id`.
- Columns: `season`, `round`, `date`; home: `home_club_id`, `home_club_name`, `home_club_goals`, `home_club_formation`, `home_club_manager_name`, `home_club_position`; away: analogous fields; extras: `competition_type`, `stadium`, `referee`, `attendance`.

## stg_player_valuations
- Purpose: Time series of player market values.
- Keys: Composite (`player_id`, `date`).
- Columns: `market_value_in_eur`, `current_club_id`, `player_club_domestic_competition_id`.

## stg_players
- Purpose: Player master data and current context.
- Key: `player_id`; refs `current_club_id`, `current_club_domestic_competition_id`.
- Columns: identity `first_name`, `last_name`, `name`; bio `country_of_birth`, `city_of_birth`, `country_of_citizenship`, `date_of_birth`; attributes `position`, `sub_position`, `foot`, `height_in_cm`; contract `contract_expiration_date`, `agent_name`; values `market_value_in_eur`, `highest_market_value_in_eur`; `last_season`.

## stg_transfers
- Purpose: Player transfers between clubs.
- Keys: `player_id` + `transfer_date` (practical uniqueness).
- Columns: `player_name`, `transfer_season`, `from_club_id`, `from_club_name`, `to_club_id`, `to_club_name`, `transfer_fee`, `market_value_in_eur`.
