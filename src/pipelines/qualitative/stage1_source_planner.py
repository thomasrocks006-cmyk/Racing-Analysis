"""
Stage 1: Source Planning Agent for Qualitative Analysis Pipeline.

This agent uses Google Gemini API to identify and prioritize information sources
that should be extracted and analyzed for each race. It maps to Categories 1-17
from the taxonomy and returns 15-25 sources per race.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import google.generativeai as genai
from pydantic import BaseModel, Field

# ============================================================================
# DATA MODELS
# ============================================================================


class SourceRecommendation(BaseModel):
    """A recommended data source for qualitative analysis."""

    source_id: str = Field(..., description="Unique identifier for the source")
    source_type: str = Field(..., description="Type of source (e.g., 'racing.com_article', 'expert_tip')")
    category: int = Field(..., ge=1, le=17, description="Taxonomy category (1-17)")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    description: str = Field(..., description="Description of what this source provides")
    url: str | None = Field(None, description="URL to the source if available")
    priority: int = Field(..., ge=1, description="Priority ranking (1=highest)")


class SourcePlan(BaseModel):
    """Complete source extraction plan for a race."""

    race_id: str = Field(..., description="Unique race identifier")
    race_name: str | None = Field(None, description="Race name")
    venue: str = Field(..., description="Venue code")
    distance: int = Field(..., description="Race distance in meters")
    sources: list[SourceRecommendation] = Field(..., description="Prioritized list of sources")
    total_sources: int = Field(..., description="Total number of sources recommended")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def high_priority_sources(self) -> list[SourceRecommendation]:
        """Get sources with relevance score >= 0.7"""
        return [s for s in self.sources if s.relevance_score >= 0.7]


# ============================================================================
# SOURCE CATEGORY MAPPING
# ============================================================================

# Category definitions from taxonomy (Categories 1-17 are qualitative)
CATEGORY_DESCRIPTIONS = {
    1: "Race Metadata (distance, venue, date, race number)",
    2: "Field Composition (number of runners, quality of opposition)",
    3: "Track Conditions (going, weather, rail position)",
    4: "Barrier Draw (post position effects)",
    5: "Jockey (rider skill, form, venue performance)",
    6: "Trainer (trainer skill, stable form)",
    7: "Weight Carried (handicap allocation)",
    8: "Market Movements (betting patterns, steam)",
    9: "Odds & Probability (market-implied odds)",
    10: "Expert Commentary (tips, analysis)",
    11: "Media Intelligence (news, stable reports)",
    12: "Gear Changes (blinkers, tongue tie, etc.)",
    13: "Barrier Trials (recent jumpouts)",
    14: "Stewards Reports (incidents, penalties)",
    15: "Breeding/Pedigree (sire/dam analysis)",
    16: "Track Bias (rail position advantage)",
    17: "Race Pace Scenario (predicted tempo)",
}

# Source type templates by category
SOURCE_TEMPLATES = {
    1: ["racing.com_race_card", "tab.com.au_race_card"],
    2: ["racing.com_field_analysis", "punters.com_field_strength"],
    3: ["racing.com_track_condition", "weatherzone_api", "racing_victoria_stewards"],
    4: ["punters.com_barrier_stats", "racing.com_barrier_analysis"],
    5: ["racing.com_jockey_stats", "tab.com.au_jockey_form"],
    6: ["racing.com_trainer_stats", "punters.com_trainer_form"],
    7: ["racing.com_weights", "racing_victoria_handicap"],
    8: ["betfair_market_moves", "tab.com.au_market_moves"],
    9: ["betfair_odds", "tab.com.au_odds", "bookmaker_odds"],
    10: ["theraces.com_expert_tips", "punters.com_analysis", "racing.com_tips"],
    11: ["twitter_stable_updates", "racing.com_news", "racing_media_articles"],
    12: ["racing.com_gear_changes", "racing_victoria_gear"],
    13: ["racing.com_barrier_trials", "racing_victoria_trials"],
    14: ["racing_victoria_stewards_reports", "racing.com_stewards"],
    15: ["racingpost_pedigree", "bloodstock_analysis"],
    16: ["punters.com_track_bias", "racing.com_track_bias"],
    17: ["punters.com_pace_map", "timeform_pace_analysis"],
}


# ============================================================================
# SOURCE PLANNING AGENT
# ============================================================================


class SourcePlanningAgent:
    """
    AI-powered agent that identifies and prioritizes information sources
    for qualitative racing analysis.

    Uses Google Gemini API to intelligently select 15-25 sources per race
    based on race characteristics, field composition, and market context.
    """

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the Source Planning Agent.

        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
            model_name: Gemini model to use (default: gemini-1.5-pro).
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def plan_sources(self, race_context: dict[str, Any]) -> SourcePlan:
        """
        Generate a prioritized list of information sources for a race.

        Args:
            race_context: Dictionary containing race details:
                - race_id (str): Unique race identifier
                - race_name (str, optional): Race name
                - venue (str): Venue code (e.g., 'FLE', 'RAN')
                - venue_name (str, optional): Full venue name
                - distance (int): Race distance in meters
                - race_type (str, optional): Race class (e.g., 'Group 1', 'Listed')
                - track_condition (str, optional): Track condition
                - field_size (int, optional): Number of runners
                - prize_money (int, optional): Prize money
                - runners (list[dict], optional): List of runner details:
                    - horse_name (str): Horse name
                    - barrier (int): Barrier draw
                    - jockey_name (str): Jockey name
                    - trainer_name (str): Trainer name
                    - odds (float, optional): Market odds
                - market_context (dict, optional): Market information:
                    - favourite_odds (float): Odds of favourite
                    - market_moves (list): Recent market movements

        Returns:
            SourcePlan: Prioritized list of 15-25 sources with relevance scores.
        """
        # Build the Gemini prompt
        prompt = self._build_prompt(race_context)

        # Call Gemini API
        response = self.model.generate_content(prompt)

        # Parse response into structured sources
        sources = self._parse_gemini_response(response.text, race_context)

        # Create and return SourcePlan
        return SourcePlan(
            race_id=race_context["race_id"],
            race_name=race_context.get("race_name"),
            venue=race_context["venue"],
            distance=race_context["distance"],
            sources=sources,
            total_sources=len(sources),
        )

    def _build_prompt(self, race_context: dict[str, Any]) -> str:
        """
        Build the Gemini API prompt from race context.

        Args:
            race_context: Race details dictionary.

        Returns:
            Formatted prompt string.
        """
        # Extract race details
        race_name = race_context.get("race_name", "Unknown Race")
        venue = race_context.get("venue_name", race_context["venue"])
        distance = race_context["distance"]
        track_condition = race_context.get("track_condition", "Unknown")
        race_type = race_context.get("race_type", "Open Handicap")
        field_size = race_context.get("field_size", "Unknown")
        prize_money = race_context.get("prize_money")

        # Build runner summary
        runners = race_context.get("runners", [])
        runner_summary = self._format_runners(runners)

        # Build market context
        market_context = race_context.get("market_context", {})
        market_summary = self._format_market_context(market_context)

        # Build comprehensive prompt
        prompt = f"""You are an expert horse racing analyst helping to identify valuable information sources for race analysis.

Given this race:
- Race: {race_name} ({race_type})
- Venue: {venue}
- Distance: {distance}m
- Track: {track_condition}
- Field Size: {field_size} runners
{f"- Prize Money: ${prize_money:,}" if prize_money else ""}

Runners:
{runner_summary}

{market_summary}

Your task: Identify the top 20 most valuable information sources for analyzing this race.

Consider:
1. Recent form and track specialists (Categories 1-7)
2. Barrier draws and track bias (Categories 4, 16)
3. Jockey/trainer changes and combinations (Categories 5-6)
4. Market movements and odds (Categories 8-9)
5. Expert commentary and media intelligence (Categories 10-11)
6. Gear changes and equipment (Category 12)
7. Barrier trials and recent work (Category 13)
8. Stewards reports and incidents (Category 14)
9. Breeding and pedigree analysis (Category 15)
10. Pace scenario and race dynamics (Category 17)

For each source, provide:
1. Source Type: Specific source identifier (e.g., "racing.com_jockey_stats", "betfair_market_moves")
2. Category: Number 1-17 from the taxonomy
3. Relevance: Score 0.0-1.0 (1.0 = critical, 0.7+ = high priority)
4. Description: Brief explanation of what insights this source provides

Format your response as a structured list of sources, with each source on a new line:
SOURCE_TYPE | CATEGORY | RELEVANCE | DESCRIPTION

Example:
racing.com_race_card | 1 | 1.0 | Complete race metadata including distance, conditions, prize money
betfair_market_moves | 8 | 0.95 | Live market movements showing betting patterns and steam
racing.com_jockey_stats | 5 | 0.85 | Jockey venue performance and recent form statistics

Prioritize sources that are:
- Highly relevant to THIS specific race
- Fresh and up-to-date
- High information quality
- Actionable for predictions

Return exactly 20 sources, ranked by importance."""

        return prompt

    def _format_runners(self, runners: list[dict]) -> str:
        """Format runner information for the prompt."""
        if not runners:
            return "Runner details not available"

        lines = []
        for i, runner in enumerate(runners[:15], 1):  # Limit to top 15 for brevity
            horse = runner.get("horse_name", "Unknown")
            barrier = runner.get("barrier", "?")
            jockey = runner.get("jockey_name", "Unknown")
            trainer = runner.get("trainer_name", "Unknown")
            odds = runner.get("odds")

            odds_str = f"${odds:.2f}" if odds else "N/A"
            lines.append(
                f"{i}. {horse} (Barrier {barrier}, {jockey}/{trainer}, Odds {odds_str})"
            )

        if len(runners) > 15:
            lines.append(f"... and {len(runners) - 15} more runners")

        return "\n".join(lines)

    def _format_market_context(self, market_context: dict) -> str:
        """Format market context for the prompt."""
        if not market_context:
            return ""

        lines = ["Market Context:"]

        if "favourite_odds" in market_context:
            lines.append(f"- Favourite: ${market_context['favourite_odds']:.2f}")

        if "market_moves" in market_context:
            moves = market_context["market_moves"]
            if moves:
                lines.append(f"- Recent moves: {len(moves)} significant movements")

        return "\n".join(lines) if len(lines) > 1 else ""

    def _parse_gemini_response(
        self, response_text: str, race_context: dict
    ) -> list[SourceRecommendation]:
        """
        Parse Gemini API response into structured SourceRecommendation objects.

        Args:
            response_text: Raw text response from Gemini.
            race_context: Original race context for reference.

        Returns:
            List of SourceRecommendation objects.
        """
        sources = []
        priority = 1

        # Split response into lines and process each
        lines = response_text.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Skip empty lines, headers, and example lines
            if not line or line.startswith("#") or "Example:" in line:
                continue

            # Skip lines that don't contain the delimiter
            if "|" not in line:
                continue

            # Parse source line: SOURCE_TYPE | CATEGORY | RELEVANCE | DESCRIPTION
            parts = [p.strip() for p in line.split("|")]

            if len(parts) >= 4:
                try:
                    source_type = parts[0]
                    category = int(parts[1])
                    relevance = float(parts[2])
                    description = parts[3]

                    # Validate category and relevance
                    if not (1 <= category <= 17):
                        continue
                    if not (0.0 <= relevance <= 1.0):
                        relevance = max(0.0, min(1.0, relevance))

                    # Generate source ID
                    source_id = f"{race_context['race_id']}_{source_type}_{priority}"

                    # Create source recommendation
                    sources.append(
                        SourceRecommendation(
                            source_id=source_id,
                            source_type=source_type,
                            category=category,
                            relevance_score=relevance,
                            description=description,
                            priority=priority,
                        )
                    )

                    priority += 1

                    # Stop at 25 sources maximum
                    if priority > 25:
                        break

                except (ValueError, IndexError):
                    # Skip malformed lines
                    continue

        # If we got fewer than 15 sources from Gemini, add default sources
        if len(sources) < 15:
            sources.extend(self._generate_default_sources(race_context, len(sources)))

        return sources[:25]  # Cap at 25 sources

    def _generate_default_sources(
        self, race_context: dict, current_count: int
    ) -> list[SourceRecommendation]:
        """
        Generate default sources when Gemini doesn't provide enough.

        Args:
            race_context: Race context dictionary.
            current_count: Number of sources already generated.

        Returns:
            List of default SourceRecommendation objects.
        """
        defaults = []
        priority = current_count + 1

        # Always include these critical sources (expanded to ensure 15+ total)
        critical_sources = [
            (1, "racing.com_race_card", 1.0, "Complete race metadata and field details"),
            (5, "racing.com_jockey_stats", 0.9, "Jockey performance and form statistics"),
            (6, "racing.com_trainer_stats", 0.9, "Trainer performance and stable form"),
            (9, "betfair_odds", 0.95, "Live market odds and probability"),
            (10, "racing.com_expert_tips", 0.85, "Expert analysis and selections"),
            (12, "racing.com_gear_changes", 0.8, "Gear and equipment changes"),
            (13, "racing.com_barrier_trials", 0.8, "Recent barrier trial performances"),
            (14, "racing_victoria_stewards", 0.75, "Stewards reports and incidents"),
            (3, "racing.com_track_condition", 0.85, "Track condition and rail position"),
            (4, "punters.com_barrier_stats", 0.75, "Barrier draw statistics for venue"),
            (8, "betfair_market_moves", 0.90, "Market movement and betting patterns"),
            (2, "racing.com_field_analysis", 0.70, "Field composition and strength analysis"),
            (7, "racing.com_weights", 0.70, "Weight allocations and handicapping"),
            (16, "punters.com_track_bias", 0.70, "Track bias and rail position effects"),
            (17, "punters.com_pace_map", 0.65, "Race pace scenario predictions"),
            (15, "racingpost_pedigree", 0.60, "Pedigree and breeding analysis"),
            (11, "twitter_stable_updates", 0.60, "Social media and stable updates"),
        ]

        race_id = race_context["race_id"]

        for category, source_type, relevance, description in critical_sources:
            if priority > 25:
                break

            source_id = f"{race_id}_{source_type}_{priority}"
            defaults.append(
                SourceRecommendation(
                    source_id=source_id,
                    source_type=source_type,
                    category=category,
                    relevance_score=relevance,
                    description=description,
                    priority=priority,
                )
            )
            priority += 1

        return defaults


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def create_race_context_from_models(
    race: Any,
    runs: list[Any],
    horses: list[Any],
    jockeys: list[Any],
    trainers: list[Any],
    market_odds: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Create a race_context dict from Pydantic models.

    Args:
        race: Race model instance
        runs: List of Run model instances
        horses: List of Horse model instances
        jockeys: List of Jockey model instances
        trainers: List of Trainer model instances
        market_odds: Optional list of MarketOdds model instances

    Returns:
        Dictionary suitable for SourcePlanningAgent.plan_sources()
    """
    # Build runners list
    runners = []
    for run in runs:
        # Find matching horse, jockey, trainer
        horse = next((h for h in horses if h.horse_id == run.horse_id), None)
        jockey = next((j for j in jockeys if j.jockey_id == run.jockey_id), None)
        trainer = next((t for t in trainers if t.trainer_id == run.trainer_id), None)

        # Find odds for this runner
        odds = None
        if market_odds:
            runner_odds = next((o for o in market_odds if o.run_id == run.run_id), None)
            if runner_odds:
                odds = float(runner_odds.odds_decimal)

        runners.append({
            "horse_name": horse.name if horse else "Unknown",
            "barrier": run.barrier,
            "jockey_name": jockey.name if jockey else "Unknown",
            "trainer_name": trainer.name if trainer else "Unknown",
            "odds": odds,
        })

    # Build market context
    market_context = {}
    if market_odds:
        # Find favourite (lowest odds)
        win_odds = [o for o in market_odds if o.odds_type.value == "win"]
        if win_odds:
            favourite = min(win_odds, key=lambda o: o.odds_decimal)
            market_context["favourite_odds"] = float(favourite.odds_decimal)

    # Build race context
    return {
        "race_id": race.race_id,
        "race_name": race.race_name,
        "venue": race.venue,
        "venue_name": race.venue_name,
        "distance": race.distance,
        "race_type": race.class_level,
        "track_condition": race.track_condition,
        "field_size": len(runs),
        "prize_money": race.prize_money,
        "runners": runners,
        "market_context": market_context,
    }
