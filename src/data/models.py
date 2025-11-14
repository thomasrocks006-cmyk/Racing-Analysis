"""
Pydantic models for racing data validation.

These models ensure data quality and type safety when ingesting racing data.
All models validate against the DuckDB schema in schema.sql.
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# ENUMS FOR VALIDATION
# ============================================================================


class SexType(str, Enum):
    """Horse sex types"""

    COLT = "colt"
    FILLY = "filly"
    GELDING = "gelding"
    MARE = "mare"
    STALLION = "stallion"


class TrackType(str, Enum):
    """Track surface types"""

    TURF = "turf"
    SYNTHETIC = "synthetic"
    DIRT = "dirt"


class OddsType(str, Enum):
    """Market odds types"""

    WIN = "win"
    PLACE = "place"


class ReportType(str, Enum):
    """Stewards report types"""

    PROTEST = "protest"
    INQUIRY = "inquiry"
    FALL = "fall"
    GENERAL = "general"


class GearType(str, Enum):
    """Gear/equipment types"""

    NONE = "none"
    BLINKERS = "blinkers"
    VISOR = "visor"
    TONGUE_TIE = "tongue-tie"
    LUGGING_BIT = "lugging-bit"
    PACIFIERS = "pacifiers"
    WINKERS = "winkers"
    VISORS = "visors"
    EAR_MUFFS = "ear-muffs"
    NOSE_ROLL = "nose-roll"
    CROSS_OVER_NOSE_BAND = "cross-over-nose-band"
    BAR_PLATES = "bar-plates"
    OTHER = "other"


# ============================================================================
# CORE MODELS
# ============================================================================


class Race(BaseModel):
    """Race event model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    race_id: str = Field(..., min_length=5, max_length=50)
    date: date
    venue: str = Field(..., min_length=2, max_length=10)
    venue_name: str | None = None
    race_number: int = Field(..., ge=1, le=12)
    race_name: str | None = None
    distance: int = Field(..., ge=800, le=5000)
    track_condition: str | None = None
    track_type: TrackType | None = None
    rail_position: str | None = None
    weather: str | None = None
    class_level: str | None = None
    prize_money: int | None = Field(None, ge=0)
    race_time: time | None = None
    actual_start_time: datetime | None = None
    field_size: int | None = Field(None, ge=2, le=24)
    race_type: str | None = None
    age_restriction: str | None = None
    sex_restriction: str | None = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    data_source: str
    is_complete: bool = False

    @field_validator("date")
    @classmethod
    def validate_race_date(cls, v: date) -> date:
        """Ensure race date is not in the future (prevent data leakage)"""
        if v > date.today():
            raise ValueError(f"Race date {v} cannot be in the future")
        return v

    @field_validator("race_id")
    @classmethod
    def validate_race_id_format(cls, v: str) -> str:
        """Validate race_id format (e.g., FLE-2025-11-09-R6)"""
        parts = v.split("-")
        if len(parts) < 4:
            raise ValueError(f"Invalid race_id format: {v}")
        return v


class Horse(BaseModel):
    """Horse model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    horse_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    foaling_date: date | None = None
    age: int | None = Field(None, ge=2, le=15)
    sex: SexType | None = None
    color: str | None = None
    sire: str | None = None
    sire_id: str | None = None
    dam: str | None = None
    dam_id: str | None = None
    dam_sire: str | None = None
    breeder: str | None = None
    country: str | None = None
    owner: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Jockey(BaseModel):
    """Jockey model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    jockey_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    active_since: date | None = None
    apprentice: bool = False
    claim_weight: Decimal | None = Field(None, ge=0, le=5.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Trainer(BaseModel):
    """Trainer model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    trainer_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    stable_location: str | None = None
    state: str | None = None
    active_since: date | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Run(BaseModel):
    """Run (race entry) model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    run_id: str = Field(..., min_length=1, max_length=100)
    race_id: str = Field(..., min_length=5, max_length=50)
    horse_id: str = Field(..., min_length=1, max_length=50)
    jockey_id: str | None = None
    trainer_id: str | None = None
    barrier: int = Field(..., ge=1, le=24)
    weight_carried: Decimal | None = Field(None, ge=48.0, le=72.0)
    handicap_weight: Decimal | None = None
    weight_penalty: Decimal | None = None
    emergency: bool = False
    scratched: bool = False
    scratched_time: datetime | None = None
    late_scratching: bool = False
    runner_number: int | None = None
    saddle_cloth: str | None = None
    starting_price_win: Decimal | None = Field(None, ge=1.01)
    starting_price_place: Decimal | None = Field(None, ge=1.01)
    created_at: datetime = Field(default_factory=datetime.now)


class Result(BaseModel):
    """Race result model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    result_id: str = Field(..., min_length=1, max_length=100)
    run_id: str = Field(..., min_length=1, max_length=100)
    race_id: str = Field(..., min_length=5, max_length=50)
    finish_position: int | None = Field(None, ge=1)
    margin: Decimal | None = Field(None, ge=0)
    total_margin: Decimal | None = Field(None, ge=0)
    race_time: Decimal | None = Field(None, gt=0)
    time_diff: Decimal | None = Field(None, ge=0)
    sectional_600m: Decimal | None = Field(None, ge=30.0, le=45.0)
    sectional_400m: Decimal | None = Field(None, ge=20.0, le=30.0)
    sectional_200m: Decimal | None = Field(None, ge=10.0, le=15.0)
    speed_rating: int | None = Field(None, ge=0, le=150)
    class_rating: int | None = Field(None, ge=0, le=150)
    beaten_margin_lengths: Decimal | None = Field(None, ge=0)
    settling_position: int | None = Field(None, ge=1)
    position_400m: int | None = Field(None, ge=1)
    position_200m: int | None = Field(None, ge=1)
    wide_run: bool = False
    checked: bool = False
    winner_or_placed: bool | None = None
    prize_money: Decimal | None = Field(None, ge=0)
    stewards_comment: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("winner_or_placed", mode="before")
    @classmethod
    def set_winner_or_placed(cls, v, info):
        """Auto-set winner_or_placed based on finish_position"""
        if v is not None:
            return v
        position = info.data.get("finish_position")
        if position is not None:
            return position <= 3
        return None


class MarketOdds(BaseModel):
    """Market odds model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    odds_id: str = Field(..., min_length=1, max_length=100)
    run_id: str = Field(..., min_length=1, max_length=100)
    race_id: str = Field(..., min_length=5, max_length=50)
    timestamp: datetime
    source: str = Field(..., min_length=1)  # 'betfair', 'tab', 'bookmaker'
    odds_type: OddsType
    odds_decimal: Decimal | None = Field(None, ge=1.01, le=1000.0)
    odds_fractional: str | None = None
    odds_american: int | None = None
    volume: Decimal | None = Field(None, ge=0)
    market_percentage: Decimal | None = Field(None, ge=0, le=100)
    rank: int | None = Field(None, ge=1)


class StewardsReport(BaseModel):
    """Stewards report model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    steward_id: str = Field(..., min_length=1, max_length=100)
    race_id: str = Field(..., min_length=5, max_length=50)
    run_id: str | None = None
    report_type: ReportType | None = None
    report_text: str | None = None
    incident_description: str | None = None
    action_taken: str | None = None
    horses_involved: list[str] | None = None
    jockeys_involved: list[str] | None = None
    severity: str | None = None  # 'low', 'medium', 'high'
    outcome: str | None = None
    published_at: datetime | None = None
    scraped_at: datetime = Field(default_factory=datetime.now)


class Gear(BaseModel):
    """Gear/equipment model"""

    model_config = ConfigDict(str_strip_whitespace=True)

    gear_id: str = Field(..., min_length=1, max_length=100)
    run_id: str = Field(..., min_length=1, max_length=100)
    gear_type: GearType
    gear_code: str | None = None
    first_time: bool = False
    removed: bool = False
    change_type: str | None = None  # 'added', 'removed', 'changed', 'same'
    previous_gear: str | None = None


# ============================================================================
# BATCH MODELS FOR BULK OPERATIONS
# ============================================================================


class RaceCard(BaseModel):
    """Complete race card (race + runs + horses + jockeys + trainers)"""

    race: Race
    runs: list[Run]
    horses: list[Horse]
    jockeys: list[Jockey]
    trainers: list[Trainer]
    gear: list[Gear] | None = None

    def validate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        total_fields = 0
        filled_fields = 0

        # Check race critical fields
        race_critical = ["distance", "track_condition", "class_level", "field_size"]
        for field in race_critical:
            total_fields += 1
            if getattr(self.race, field) is not None:
                filled_fields += 1

        # Check runs critical fields
        runs_critical = ["barrier", "weight_carried"]
        for run in self.runs:
            for field in runs_critical:
                total_fields += 1
                if getattr(run, field) is not None:
                    filled_fields += 1

        return (filled_fields / total_fields * 100) if total_fields > 0 else 0.0


class RaceResult(BaseModel):
    """Complete race result"""

    race: Race
    results: list[Result]

    @field_validator("results")
    @classmethod
    def validate_results(cls, v: list[Result]) -> list[Result]:
        """Ensure results are ordered by finish position"""
        return sorted(v, key=lambda x: x.finish_position or 999)


# ============================================================================
# SIMPLIFIED SCRAPED DATA MODELS (No IDs required)
# ============================================================================


class ScrapedHorse(BaseModel):
    """Simplified horse model for scraped data (no ID required)"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    age: int | None = Field(None, ge=2, le=15)
    sex: SexType | None = None
    color: str | None = None
    sire: str | None = None
    dam: str | None = None


class ScrapedJockey(BaseModel):
    """Simplified jockey model for scraped data (no ID required)"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    apprentice: bool = False
    claim_weight: Decimal | None = Field(None, ge=0, le=5.0)


class ScrapedTrainer(BaseModel):
    """Simplified trainer model for scraped data (no ID required)"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100)
    stable_location: str | None = None


class ScrapedRun(BaseModel):
    """Simplified run model for scraped data (no IDs required)"""

    model_config = ConfigDict(str_strip_whitespace=True)

    race_id: str = Field(..., min_length=5, max_length=50)
    horse_name: str = Field(..., min_length=1, max_length=100)
    jockey_name: str = Field(..., min_length=1, max_length=100)
    trainer_name: str = Field(..., min_length=1, max_length=100)
    barrier: int | None = Field(None, ge=1, le=24)
    weight: Decimal | None = Field(None, ge=48.0, le=72.0)
    handicap_rating: int | None = None
    emergency: bool = False
    emergency_number: int | None = None
    scratched: bool = False


class ScrapedGear(BaseModel):
    """Simplified gear model for scraped data (no IDs required)"""

    model_config = ConfigDict(str_strip_whitespace=True)

    race_id: str = Field(..., min_length=5, max_length=50)
    horse_name: str = Field(..., min_length=1, max_length=100)
    gear_type: GearType
    gear_description: str | None = None
    is_first_time: bool = False
    gear_changes: str | None = None


class ScrapedRaceCard(BaseModel):
    """Complete race card using scraped data models (no IDs required)"""

    race: Race
    runs: list[ScrapedRun]
    horses: list[ScrapedHorse]
    jockeys: list[ScrapedJockey]
    trainers: list[ScrapedTrainer]
    gear: list[ScrapedGear] | None = None

    def validate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        total_fields = 0
        filled_fields = 0

        # Check race critical fields
        race_critical = ["distance", "track_condition", "class_level", "field_size"]
        for field in race_critical:
            total_fields += 1
            if getattr(self.race, field) is not None:
                filled_fields += 1

        # Check runs critical fields
        runs_critical = ["barrier", "weight"]
        for run in self.runs:
            for field in runs_critical:
                total_fields += 1
                if getattr(run, field) is not None:
                    filled_fields += 1

        return (filled_fields / total_fields * 100) if total_fields > 0 else 0.0
