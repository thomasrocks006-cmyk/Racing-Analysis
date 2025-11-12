-- Racing Analysis System - DuckDB Database Schema
-- Created: 2025-11-12
-- Purpose: Store racing data for quantitative analysis (Categories 18-21)

-- ============================================================================
-- CORE RACING TABLES
-- ============================================================================

-- Races: One row per race event
CREATE TABLE IF NOT EXISTS races (
    race_id VARCHAR PRIMARY KEY,              -- Unique identifier (e.g., 'FLE-2025-11-09-R6')
    date DATE NOT NULL,                       -- Race date
    venue VARCHAR NOT NULL,                   -- Track code (e.g., 'FLE', 'RAL', 'CBR')
    venue_name VARCHAR,                       -- Full venue name (e.g., 'Flemington')
    race_number INTEGER NOT NULL,             -- Race number on card (1-12)
    race_name VARCHAR,                        -- Race name (e.g., 'Melbourne Cup')
    distance INTEGER NOT NULL,                -- Distance in meters
    track_condition VARCHAR,                  -- Going (e.g., 'Good 4', 'Heavy 8')
    track_type VARCHAR,                       -- Surface type ('turf', 'synthetic', 'dirt')
    rail_position VARCHAR,                    -- Rail position (e.g., 'True', '+6m')
    weather VARCHAR,                          -- Weather conditions
    class_level VARCHAR,                      -- Race class (e.g., 'G1', 'Listed', 'BM78')
    prize_money INTEGER,                      -- Total prize pool
    race_time TIME,                           -- Scheduled start time
    actual_start_time TIMESTAMP,              -- Actual start timestamp
    field_size INTEGER,                       -- Number of runners
    race_type VARCHAR,                        -- Type (e.g., 'handicap', 'weight-for-age')
    age_restriction VARCHAR,                  -- Age limits (e.g., '3yo+')
    sex_restriction VARCHAR,                  -- Sex limits (e.g., 'fillies-mares')
    scraped_at TIMESTAMP NOT NULL,            -- When data was scraped
    data_source VARCHAR NOT NULL,             -- Source (e.g., 'racing.com')
    is_complete BOOLEAN DEFAULT FALSE,        -- Data completeness flag
    -- Note: Date validation should be done in application layer (Pydantic)
    CONSTRAINT races_distance_check CHECK (distance >= 800 AND distance <= 5000),
    CONSTRAINT races_field_size_check CHECK (field_size >= 2 AND field_size <= 24)
);

-- Horses: One row per horse (master table)
CREATE TABLE IF NOT EXISTS horses (
    horse_id VARCHAR PRIMARY KEY,             -- Unique identifier
    name VARCHAR NOT NULL,                    -- Horse name
    foaling_date DATE,                        -- Birth date
    age INTEGER,                              -- Current age
    sex VARCHAR,                              -- 'colt', 'filly', 'gelding', 'mare', 'stallion'
    color VARCHAR,                            -- Coat color
    sire VARCHAR,                             -- Father's name
    sire_id VARCHAR,                          -- Father's ID
    dam VARCHAR,                              -- Mother's name
    dam_id VARCHAR,                           -- Mother's ID
    dam_sire VARCHAR,                         -- Maternal grandfather
    breeder VARCHAR,                          -- Breeder name
    country VARCHAR,                          -- Country of birth
    owner VARCHAR,                            -- Current owner
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT horses_sex_check CHECK (sex IN ('colt', 'filly', 'gelding', 'mare', 'stallion'))
);

-- Jockeys: One row per jockey
CREATE TABLE IF NOT EXISTS jockeys (
    jockey_id VARCHAR PRIMARY KEY,            -- Unique identifier
    name VARCHAR NOT NULL,                    -- Jockey name
    active_since DATE,                        -- Career start date
    apprentice BOOLEAN DEFAULT FALSE,         -- Apprentice status
    claim_weight DECIMAL(3,1),                -- Apprentice claim (e.g., 3.0 kg)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainers: One row per trainer
CREATE TABLE IF NOT EXISTS trainers (
    trainer_id VARCHAR PRIMARY KEY,           -- Unique identifier
    name VARCHAR NOT NULL,                    -- Trainer name
    stable_location VARCHAR,                  -- Stable base (e.g., 'Flemington')
    state VARCHAR,                            -- State/region
    active_since DATE,                        -- Career start date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Runs: One row per horse in a race (race entries)
CREATE TABLE IF NOT EXISTS runs (
    run_id VARCHAR PRIMARY KEY,               -- Unique identifier (race_id + runner number)
    race_id VARCHAR NOT NULL,                 -- FK to races
    horse_id VARCHAR NOT NULL,                -- FK to horses
    jockey_id VARCHAR,                        -- FK to jockeys
    trainer_id VARCHAR,                       -- FK to trainers
    barrier INTEGER NOT NULL,                 -- Barrier draw (1-24)
    weight_carried DECIMAL(4,1),              -- Weight in kg (e.g., 58.5)
    handicap_weight DECIMAL(4,1),             -- Allocated handicap weight
    weight_penalty DECIMAL(3,1),              -- Penalty/bonus
    emergency BOOLEAN DEFAULT FALSE,          -- Emergency runner flag
    scratched BOOLEAN DEFAULT FALSE,          -- Scratched flag
    scratched_time TIMESTAMP,                 -- When scratched
    late_scratching BOOLEAN DEFAULT FALSE,    -- Late scratching (< 1 hour)
    runner_number INTEGER,                    -- Number on race card
    saddle_cloth VARCHAR,                     -- Saddle cloth number/color
    starting_price_win DECIMAL(6,2),          -- SP odds (win)
    starting_price_place DECIMAL(6,2),        -- SP odds (place)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (horse_id) REFERENCES horses(horse_id),
    FOREIGN KEY (jockey_id) REFERENCES jockeys(jockey_id),
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id),
    CONSTRAINT runs_barrier_check CHECK (barrier >= 1 AND barrier <= 24),
    CONSTRAINT runs_weight_check CHECK (weight_carried >= 48.0 AND weight_carried <= 72.0)
);

-- Results: One row per run result (race outcomes)
CREATE TABLE IF NOT EXISTS results (
    result_id VARCHAR PRIMARY KEY,            -- Unique identifier
    run_id VARCHAR NOT NULL,                  -- FK to runs
    race_id VARCHAR NOT NULL,                 -- FK to races (denormalized for query speed)
    finish_position INTEGER,                  -- Final position (1 = winner, NULL = DNF)
    margin DECIMAL(5,2),                      -- Margin in lengths (to horse ahead)
    total_margin DECIMAL(5,2),                -- Cumulative margin to winner
    race_time DECIMAL(6,3),                   -- Winning time (seconds)
    time_diff DECIMAL(5,3),                   -- Time behind winner (seconds)
    sectional_600m DECIMAL(5,2),              -- Last 600m sectional (seconds)
    sectional_400m DECIMAL(5,2),              -- Last 400m sectional
    sectional_200m DECIMAL(5,2),              -- Last 200m sectional
    speed_rating INTEGER,                     -- Speed rating (0-130)
    class_rating INTEGER,                     -- Class-adjusted rating
    beaten_margin_lengths DECIMAL(5,2),       -- Total margin (lengths)
    settling_position INTEGER,                -- Position at 800m/halfway
    position_400m INTEGER,                    -- Position at 400m to go
    position_200m INTEGER,                    -- Position at 200m to go
    wide_run BOOLEAN DEFAULT FALSE,           -- Ran wide in straight
    checked BOOLEAN DEFAULT FALSE,            -- Checked/interfered during race
    winner_or_placed BOOLEAN,                 -- Win or place (1-3)
    prize_money DECIMAL(10,2),                -- Prize money won
    stewards_comment TEXT,                    -- Stewards' comment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    CONSTRAINT results_position_check CHECK (finish_position >= 1 OR finish_position IS NULL),
    CONSTRAINT results_margin_check CHECK (margin >= 0 OR margin IS NULL),
    CONSTRAINT results_sectional_check CHECK (
        (sectional_600m >= 30.0 AND sectional_600m <= 45.0) OR sectional_600m IS NULL
    )
);

-- Market Odds: Market prices over time
CREATE TABLE IF NOT EXISTS market_odds (
    odds_id VARCHAR PRIMARY KEY,              -- Unique identifier
    run_id VARCHAR NOT NULL,                  -- FK to runs
    race_id VARCHAR NOT NULL,                 -- FK to races (denormalized)
    timestamp TIMESTAMP NOT NULL,             -- When odds recorded
    source VARCHAR NOT NULL,                  -- 'betfair', 'tab', 'bookmaker'
    odds_type VARCHAR NOT NULL,               -- 'win', 'place'
    odds_decimal DECIMAL(6,2),                -- Decimal odds (e.g., 3.50)
    odds_fractional VARCHAR,                  -- Fractional odds (e.g., '5/2')
    odds_american INTEGER,                    -- American odds (e.g., +250)
    volume DECIMAL(12,2),                     -- Volume traded (Betfair only)
    market_percentage DECIMAL(5,2),           -- Market %
    rank INTEGER,                             -- Rank in market (1 = favourite)
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    CONSTRAINT odds_type_check CHECK (odds_type IN ('win', 'place')),
    CONSTRAINT odds_decimal_check CHECK (odds_decimal >= 1.01 AND odds_decimal <= 1000.0)
);

-- Stewards Reports: Official race incident reports
CREATE TABLE IF NOT EXISTS stewards (
    steward_id VARCHAR PRIMARY KEY,           -- Unique identifier
    race_id VARCHAR NOT NULL,                 -- FK to races
    run_id VARCHAR,                           -- FK to runs (if horse-specific)
    report_type VARCHAR,                      -- 'protest', 'inquiry', 'fall', 'general'
    report_text TEXT,                         -- Full report text
    incident_description TEXT,                -- Incident summary
    action_taken TEXT,                        -- Stewards' action (e.g., 'suspension')
    horses_involved VARCHAR[],                -- List of horse names involved
    jockeys_involved VARCHAR[],               -- List of jockey names involved
    severity VARCHAR,                         -- 'low', 'medium', 'high'
    outcome VARCHAR,                          -- 'no action', 'penalty', 'disqualification'
    published_at TIMESTAMP,                   -- Official publication time
    scraped_at TIMESTAMP NOT NULL,            -- When scraped
    FOREIGN KEY (race_id) REFERENCES races(race_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Gear: Equipment and gear changes
CREATE TABLE IF NOT EXISTS gear (
    gear_id VARCHAR PRIMARY KEY,              -- Unique identifier
    run_id VARCHAR NOT NULL,                  -- FK to runs
    gear_type VARCHAR NOT NULL,               -- 'blinkers', 'tongue-tie', 'lugging-bit', etc.
    gear_code VARCHAR,                        -- Abbreviated code (e.g., 'B', 'TT', 'LB')
    first_time BOOLEAN DEFAULT FALSE,         -- First time wearing this gear
    removed BOOLEAN DEFAULT FALSE,            -- Gear removed (was worn previously)
    change_type VARCHAR,                      -- 'added', 'removed', 'changed', 'same'
    previous_gear VARCHAR,                    -- Previous gear configuration
    FOREIGN KEY (run_id) REFERENCES runs(run_id),
    CONSTRAINT gear_type_check CHECK (gear_type IN (
        'blinkers', 'tongue-tie', 'lugging-bit', 'pacifiers', 'winkers',
        'visors', 'ear-muffs', 'nose-roll', 'cross-over-nose-band', 'bar-plates'
    ))
);

-- ============================================================================
-- INDEXES FOR QUERY PERFORMANCE
-- ============================================================================

-- Races indexes
CREATE INDEX IF NOT EXISTS idx_races_date ON races(date);
CREATE INDEX IF NOT EXISTS idx_races_venue ON races(venue);
CREATE INDEX IF NOT EXISTS idx_races_date_venue ON races(date, venue);
CREATE INDEX IF NOT EXISTS idx_races_class ON races(class_level);

-- Runs indexes
CREATE INDEX IF NOT EXISTS idx_runs_race_id ON runs(race_id);
CREATE INDEX IF NOT EXISTS idx_runs_horse_id ON runs(horse_id);
CREATE INDEX IF NOT EXISTS idx_runs_jockey_id ON runs(jockey_id);
CREATE INDEX IF NOT EXISTS idx_runs_trainer_id ON runs(trainer_id);
CREATE INDEX IF NOT EXISTS idx_runs_scratched ON runs(scratched);

-- Results indexes
CREATE INDEX IF NOT EXISTS idx_results_run_id ON results(run_id);
CREATE INDEX IF NOT EXISTS idx_results_race_id ON results(race_id);
CREATE INDEX IF NOT EXISTS idx_results_position ON results(finish_position);
CREATE INDEX IF NOT EXISTS idx_results_winner ON results(winner_or_placed);

-- Market odds indexes
CREATE INDEX IF NOT EXISTS idx_market_run_id ON market_odds(run_id);
CREATE INDEX IF NOT EXISTS idx_market_race_id ON market_odds(race_id);
CREATE INDEX IF NOT EXISTS idx_market_timestamp ON market_odds(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_source ON market_odds(source, odds_type);

-- Stewards indexes
CREATE INDEX IF NOT EXISTS idx_stewards_race_id ON stewards(race_id);
CREATE INDEX IF NOT EXISTS idx_stewards_type ON stewards(report_type);

-- Gear indexes
CREATE INDEX IF NOT EXISTS idx_gear_run_id ON gear(run_id);
CREATE INDEX IF NOT EXISTS idx_gear_first_time ON gear(first_time);
CREATE INDEX IF NOT EXISTS idx_gear_type ON gear(gear_type);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete race card view (all runners with details)
CREATE OR REPLACE VIEW v_race_card AS
SELECT
    r.race_id,
    r.date,
    r.venue,
    r.venue_name,
    r.race_number,
    r.race_name,
    r.distance,
    r.track_condition,
    r.class_level,
    runs.run_id,
    runs.barrier,
    runs.runner_number,
    runs.weight_carried,
    runs.scratched,
    h.name AS horse_name,
    h.age,
    h.sex,
    j.name AS jockey_name,
    t.name AS trainer_name,
    runs.starting_price_win,
    runs.starting_price_place
FROM races r
JOIN runs ON runs.race_id = r.race_id
JOIN horses h ON h.horse_id = runs.horse_id
LEFT JOIN jockeys j ON j.jockey_id = runs.jockey_id
LEFT JOIN trainers t ON t.trainer_id = runs.trainer_id
WHERE runs.scratched = FALSE;

-- Race results view (with sectionals)
CREATE OR REPLACE VIEW v_race_results AS
SELECT
    r.race_id,
    r.date,
    r.venue,
    r.race_number,
    r.distance,
    r.track_condition,
    res.finish_position,
    h.name AS horse_name,
    res.margin,
    res.total_margin,
    res.race_time,
    res.sectional_600m,
    res.sectional_400m,
    res.sectional_200m,
    res.speed_rating,
    j.name AS jockey_name,
    t.name AS trainer_name,
    runs.weight_carried,
    runs.barrier
FROM races r
JOIN results res ON res.race_id = r.race_id
JOIN runs ON runs.run_id = res.run_id
JOIN horses h ON h.horse_id = runs.horse_id
LEFT JOIN jockeys j ON j.jockey_id = runs.jockey_id
LEFT JOIN trainers t ON t.trainer_id = runs.trainer_id
ORDER BY r.race_id, res.finish_position;

-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================

-- Check for races with missing critical data
CREATE OR REPLACE VIEW v_incomplete_races AS
SELECT
    race_id,
    date,
    venue,
    CASE
        WHEN distance IS NULL THEN 'Missing distance'
        WHEN track_condition IS NULL THEN 'Missing track condition'
        WHEN class_level IS NULL THEN 'Missing class level'
        WHEN field_size IS NULL THEN 'Missing field size'
        ELSE 'Unknown issue'
    END AS issue
FROM races
WHERE is_complete = FALSE
   OR distance IS NULL
   OR track_condition IS NULL;

-- Check for runs with missing key data
CREATE OR REPLACE VIEW v_incomplete_runs AS
SELECT
    run_id,
    race_id,
    CASE
        WHEN horse_id IS NULL THEN 'Missing horse'
        WHEN barrier IS NULL THEN 'Missing barrier'
        WHEN weight_carried IS NULL THEN 'Missing weight'
        ELSE 'Unknown issue'
    END AS issue
FROM runs
WHERE horse_id IS NULL
   OR barrier IS NULL
   OR weight_carried IS NULL;
