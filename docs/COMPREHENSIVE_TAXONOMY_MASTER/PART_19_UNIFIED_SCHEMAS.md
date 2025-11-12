# Master Taxonomy - Part 19: Unified Data Schemas & Export Formats

**Document Purpose:** Complete data models for all 21 categories with export specifications
**Pipeline Usage:** Both pipelines (data structure foundation)
**Implementation Priority:** Phase 1 Week 8

---

## COMPLETE UNIFIED SCHEMA

### Master Race Data Structure
```python
master_race_schema = {
    "race_metadata": {
        "race_id": str,
        "venue": str,
        "distance": int,
        "race_date": "YYYY-MM-DD",
        "race_time": "HH:MM",
        "race_class": str,
        "prize_money": int,
        "field_size": int
    },

    "track_conditions": {
        "track_condition_index": int,  # 1-10
        "track_rating": str,  # "Good 3"
        "rail_position": str,
        "track_bias_score": float,  # -20 to +20
        "weather": {
            "temperature_c": float,
            "humidity_pct": float,
            "wind_speed_kmh": float,
            "comfort_index": float
        }
    },

    "horses": [
        {
            "horse_name": str,
            "barrier": int,
            "weight_kg": float,
            "jockey": str,
            "trainer": str,

            "historical_performance": {
                "form_string": str,  # "1234x"
                "form_score": float,  # 0-100
                "last_5_starts": list,
                "career_stats": {
                    "starts": int,
                    "wins": int,
                    "places": int,
                    "win_pct": float,
                    "prize_money": int
                },
                "first_up_stats": {
                    "first_up_starts": int,
                    "first_up_wins": int,
                    "first_up_win_pct": float
                },
                "consistency_score": float  # 0-100
            },

            "speed_ratings": {
                "timeform_rating": float,
                "rating_vs_field_avg": float,
                "is_top_rated": bool,
                "recent_avg_speed": float,
                "class_adjusted_rating": float,
                "condition_adjusted_rating": float
            },

            "class_ratings": {
                "official_rating": int,
                "rating_band": str,
                "class_drop": bool,
                "class_change": int
            },

            "suitability": {
                "venue_win_pct": float,
                "venue_specialist": bool,
                "distance_win_pct": float,
                "distance_specialist": bool,
                "combo_specialist": bool
            },

            "intangibles": {
                "fitness_rating": int,  # 1-10
                "preparation_quality_score": float,  # 0-100
                "peak_window_index": float,  # 0-1
                "in_peak_window": bool
            },

            "chemistry": {
                "jockey_trainer_partnership": {
                    "partnership_rides": int,
                    "partnership_win_pct": float,
                    "synergy_score": float,
                    "strong_partnership": bool
                },
                "jockey_horse_combo": {
                    "combo_rides": int,
                    "combo_win_pct": float,
                    "proven_combination": bool
                },
                "three_way_synergy": {
                    "three_way_rides": int,
                    "three_way_win_pct": float,
                    "dream_team": bool
                }
            },

            "market_data": {
                "opening_odds": float,
                "current_odds": float,
                "odds_movement_pct": float,
                "market_move": str,  # "steamer"/"drifter"/"stable"
                "betfair_matched_volume": float,
                "implied_probability": float
            },

            "pace_sectionals": {
                "expected_settling_position": int,
                "avg_settling_position": float,
                "run_style": str,
                "closing_speed_mps": float,
                "600m_split": float,
                "400m_split": float,
                "200m_split": float
            },

            "gear_trials": {
                "gear_changes": {
                    "first_time_blinkers": bool,
                    "any_gear_change": bool,
                    "expected_impact": float
                },
                "trial_data": {
                    "had_trial": bool,
                    "trial_performance_score": float,  # 0-100
                    "trial_freshness_score": float,  # 0-100
                    "days_since_trial": int
                }
            },

            "pedigree": {
                "sire_name": str,
                "dam_name": str,
                "sire_progeny_win_pct": float,
                "distance_suited_by_pedigree": bool,
                "wet_track_sire": bool
            },

            "predictions": {
                "win_probability": float,  # 0-1
                "place_probability": float,
                "confidence_score": float,  # 0-1
                "selection_grade": str,  # A+, A, B, C, D, F
                "recommendation": str
            }
        }
    ]
}
```

---

## EXPORT FORMATS

### JSON Export
```python
def export_to_json(race_data, filepath):
    """Export race data to JSON"""
    import json

    with open(filepath, 'w') as f:
        json.dump(race_data, f, indent=2, default=str)
```

### CSV Export (Flattened for ML)
```python
def export_to_csv_flat(race_data, filepath):
    """Export flattened race data for ML pipeline"""
    import pandas as pd

    rows = []

    for horse in race_data['horses']:
        row = {
            # Race metadata
            'race_id': race_data['race_metadata']['race_id'],
            'venue': race_data['race_metadata']['venue'],
            'distance': race_data['race_metadata']['distance'],
            'race_class': race_data['race_metadata']['race_class'],

            # Horse basics
            'horse_name': horse['horse_name'],
            'barrier': horse['barrier'],
            'weight_kg': horse['weight_kg'],
            'jockey': horse['jockey'],
            'trainer': horse['trainer'],

            # Performance
            'form_score': horse['historical_performance']['form_score'],
            'career_win_pct': horse['historical_performance']['career_stats']['win_pct'],
            'first_up_win_pct': horse['historical_performance']['first_up_stats']['first_up_win_pct'],

            # Speed & class
            'timeform_rating': horse['speed_ratings']['timeform_rating'],
            'rating_vs_field_avg': horse['speed_ratings']['rating_vs_field_avg'],
            'is_top_rated': int(horse['speed_ratings']['is_top_rated']),
            'official_rating': horse['class_ratings']['official_rating'],

            # Suitability
            'venue_specialist': int(horse['suitability']['venue_specialist']),
            'distance_specialist': int(horse['suitability']['distance_specialist']),

            # Fitness
            'fitness_rating': horse['intangibles']['fitness_rating'],
            'in_peak_window': int(horse['intangibles']['in_peak_window']),

            # Chemistry
            'dream_team': int(horse['chemistry']['three_way_synergy']['dream_team']),
            'partnership_win_pct': horse['chemistry']['jockey_trainer_partnership']['partnership_win_pct'],

            # Market
            'current_odds': horse['market_data']['current_odds'],
            'market_move': horse['market_data']['market_move'],
            'implied_probability': horse['market_data']['implied_probability'],

            # Pace
            'expected_settling_position': horse['pace_sectionals']['expected_settling_position'],
            'closing_speed_mps': horse['pace_sectionals']['closing_speed_mps'],

            # Gear & trials
            'first_time_blinkers': int(horse['gear_trials']['gear_changes']['first_time_blinkers']),
            'had_trial': int(horse['gear_trials']['trial_data']['had_trial']),
            'trial_performance_score': horse['gear_trials']['trial_data']['trial_performance_score'],

            # Target variable (if available)
            'win': horse.get('actual_result', {}).get('position') == 1 if 'actual_result' in horse else None
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False)

    return df
```

### Database Schema (PostgreSQL)
```sql
CREATE TABLE races (
    race_id VARCHAR(50) PRIMARY KEY,
    venue VARCHAR(100),
    distance INT,
    race_date DATE,
    race_time TIME,
    race_class VARCHAR(50),
    prize_money INT,
    field_size INT,
    track_condition_index INT,
    track_rating VARCHAR(20),
    rail_position VARCHAR(50),
    track_bias_score FLOAT,
    temperature_c FLOAT,
    humidity_pct FLOAT
);

CREATE TABLE horses (
    entry_id SERIAL PRIMARY KEY,
    race_id VARCHAR(50) REFERENCES races(race_id),
    horse_name VARCHAR(100),
    barrier INT,
    weight_kg FLOAT,
    jockey VARCHAR(100),
    trainer VARCHAR(100),

    -- Performance
    form_score FLOAT,
    career_starts INT,
    career_wins INT,
    career_win_pct FLOAT,
    first_up_win_pct FLOAT,
    consistency_score FLOAT,

    -- Ratings
    timeform_rating FLOAT,
    rating_vs_field_avg FLOAT,
    is_top_rated BOOLEAN,
    official_rating INT,
    class_drop BOOLEAN,

    -- Suitability
    venue_specialist BOOLEAN,
    distance_specialist BOOLEAN,
    fitness_rating INT,
    in_peak_window BOOLEAN,

    -- Chemistry
    dream_team BOOLEAN,
    partnership_win_pct FLOAT,

    -- Market
    current_odds FLOAT,
    market_move VARCHAR(20),
    implied_probability FLOAT,

    -- Pace & sectionals
    expected_settling_position INT,
    closing_speed_mps FLOAT,

    -- Gear & trials
    first_time_blinkers BOOLEAN,
    had_trial BOOLEAN,
    trial_performance_score FLOAT,

    -- Predictions
    win_probability FLOAT,
    place_probability FLOAT,
    confidence_score FLOAT,
    selection_grade VARCHAR(5),

    -- Actual result (populated after race)
    actual_position INT,
    actual_margin FLOAT,
    actual_time FLOAT
);

CREATE INDEX idx_races_date ON races(race_date);
CREATE INDEX idx_horses_race ON horses(race_id);
CREATE INDEX idx_horses_name ON horses(horse_name);
CREATE INDEX idx_jockey ON horses(jockey);
CREATE INDEX idx_trainer ON horses(trainer);
```

---

**Document Complete: Part 19 (Unified Data Schemas)**
**Next: Part 20 (Implementation Roadmap Phase 1)**
