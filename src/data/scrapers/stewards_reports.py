"""
Stewards Reports Parser for Racing Victoria and Racing NSW.

This scraper:
- Parses PDF stewards reports using pdfplumber + PyPDF2
- Extracts: vet checks, track bias, incidents, rail position
- Handles robust error recovery for malformed PDFs
- Sources: Racing Victoria, Racing NSW

Usage:
    from src.data.scrapers.stewards_reports import StewardsReportParser

    parser = StewardsReportParser()
    report_data = parser.parse_pdf_report(pdf_path)
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pdfplumber
import requests
from PyPDF2 import PdfReader

from src.data.models import ReportType, StewardsReport

logger = logging.getLogger(__name__)


class StewardsReportParser:
    """
    Parser for stewards' reports from Racing Victoria and Racing NSW.

    Uses dual PDF parsing strategy:
    1. pdfplumber for text extraction (primary)
    2. PyPDF2 for fallback and metadata extraction

    Confidence indicators are included in extracted data to guide
    downstream usage.
    """

    # Racing Victoria URLs (CONFIDENCE: HIGH - confirmed active Nov 2025)
    RV_BASE_URL = "https://www.racingvictoria.com.au"
    RV_REPORTS_URL = f"{RV_BASE_URL}/the-sport/stewards-reports"

    # Racing NSW URLs (CONFIDENCE: HIGH - confirmed active Nov 2025)
    RNSW_BASE_URL = "https://www.racingnsw.com.au"
    RNSW_REPORTS_URL = f"{RNSW_BASE_URL}/stewards-reports"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/pdf,text/html,application/xhtml+xml",
    }

    def __init__(self, delay_between_requests: float = 2.0):
        """
        Initialize stewards report parser.

        Args:
            delay_between_requests: Delay between PDF downloads (be polite!)
        """
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def parse_pdf_report(self, pdf_path: str | Path) -> dict[str, Any]:
        """
        Parse a stewards report PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted data:
            {
                'venue': str,
                'date': date,
                'vet_checks': list[dict],  # Pre-race vet scratches
                'track_bias': str | None,  # Detected track bias
                'incidents': list[dict],    # Race incidents
                'rail_position': str | None,
                'track_condition': str | None,
                'weather': str | None,
                'confidence': float,        # Extraction confidence (0-1)
                'raw_text': str,           # Full text for debugging
            }

        Example:
            >>> parser = StewardsReportParser()
            >>> data = parser.parse_pdf_report("flemington_2024-11-05.pdf")
            >>> print(f"Found {len(data['incidents'])} incidents")
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Parsing stewards report: {pdf_path.name}")

        try:
            # Primary extraction: pdfplumber (better for complex layouts)
            extracted_data = self._extract_with_pdfplumber(pdf_path)

            # If primary fails, try PyPDF2 fallback
            if extracted_data.get("confidence", 0) < 0.3:
                logger.warning("Low confidence from pdfplumber, trying PyPDF2 fallback")
                fallback_data = self._extract_with_pypdf2(pdf_path)
                extracted_data = self._merge_extraction_results(
                    extracted_data, fallback_data
                )

            # Parse structured data from raw text
            parsed_data = self._parse_structured_data(extracted_data["raw_text"])
            extracted_data.update(parsed_data)

            logger.info(
                f"✓ Parsed report: {len(parsed_data.get('incidents', []))} incidents, "
                f"{len(parsed_data.get('vet_checks', []))} vet checks, "
                f"confidence={extracted_data.get('confidence', 0):.2f}"
            )

            return extracted_data

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path.name}: {e}", exc_info=True)
            return {
                "error": str(e),
                "confidence": 0.0,
                "raw_text": "",
            }

    def _extract_with_pdfplumber(self, pdf_path: Path) -> dict[str, Any]:
        """
        Extract text using pdfplumber (primary method).

        CONFIDENCE: HIGH for Racing Victoria/NSW PDFs
        pdfplumber handles complex layouts better than PyPDF2
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_blocks = []

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        if text:
                            text_blocks.append(text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        continue

                full_text = "\n".join(text_blocks)

                # Calculate confidence based on text quality
                confidence = self._calculate_extraction_confidence(full_text)

                return {
                    "raw_text": full_text,
                    "page_count": len(pdf.pages),
                    "confidence": confidence,
                    "method": "pdfplumber",
                }

        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return {
                "raw_text": "",
                "confidence": 0.0,
                "method": "pdfplumber",
                "error": str(e),
            }

    def _extract_with_pypdf2(self, pdf_path: Path) -> dict[str, Any]:
        """
        Extract text using PyPDF2 (fallback method).

        CONFIDENCE: MEDIUM - works for simple layouts
        Less reliable for complex tables but good for plain text
        """
        try:
            reader = PdfReader(str(pdf_path))
            text_blocks = []

            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                    if text:
                        text_blocks.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue

            full_text = "\n".join(text_blocks)
            confidence = self._calculate_extraction_confidence(full_text)

            return {
                "raw_text": full_text,
                "page_count": len(reader.pages),
                "confidence": confidence,
                "method": "PyPDF2",
            }

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return {
                "raw_text": "",
                "confidence": 0.0,
                "method": "PyPDF2",
                "error": str(e),
            }

    def _merge_extraction_results(
        self, primary: dict[str, Any], fallback: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Merge results from primary and fallback extraction.

        Strategy: Use whichever has higher confidence
        """
        if primary.get("confidence", 0) >= fallback.get("confidence", 0):
            return primary
        else:
            logger.info(f"Using fallback method ({fallback.get('method')})")
            return fallback

    def _calculate_extraction_confidence(self, text: str) -> float:
        """
        Calculate confidence score for extracted text.

        Heuristics:
        - Length: More text = higher confidence
        - Structure: Presence of keywords
        - Formatting: Line breaks, spacing

        Returns: 0.0 to 1.0
        """
        if not text or len(text) < 50:
            return 0.0

        confidence = 0.0

        # Length score (max 0.3)
        length_score = min(len(text) / 5000.0, 1.0) * 0.3
        confidence += length_score

        # Keyword presence (max 0.4)
        keywords = [
            "steward", "inquiry", "protest", "vet", "scratched",
            "track", "rail", "incident", "interference"
        ]
        keyword_count = sum(1 for kw in keywords if kw.lower() in text.lower())
        keyword_score = (keyword_count / len(keywords)) * 0.4
        confidence += keyword_score

        # Structure score (max 0.3)
        has_dates = bool(re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text))
        has_race_numbers = bool(re.search(r"[Rr]ace\s*\d+|R\d+", text))
        has_line_breaks = text.count("\n") > 10

        structure_score = (
            (0.1 if has_dates else 0) +
            (0.1 if has_race_numbers else 0) +
            (0.1 if has_line_breaks else 0)
        )
        confidence += structure_score

        return min(confidence, 1.0)

    def _parse_structured_data(self, text: str) -> dict[str, Any]:
        """
        Parse structured data from raw text.

        Extracts:
        - Venue and date
        - Vet checks (pre-race scratches)
        - Track bias reports
        - Incidents (falls, interference, protests)
        - Rail position
        - Track condition

        CONFIDENCE: MEDIUM - regex-based extraction is brittle
        but works well for standardized reports
        """
        parsed = {
            "venue": None,
            "date": None,
            "vet_checks": [],
            "track_bias": None,
            "incidents": [],
            "rail_position": None,
            "track_condition": None,
            "weather": None,
        }

        # Extract venue (CONFIDENCE: HIGH for standard formats)
        venue_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:Race\s*)?(?:Meeting|Races?)",
            r"Venue:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        ]
        for pattern in venue_patterns:
            match = re.search(pattern, text)
            if match:
                parsed["venue"] = match.group(1).strip()
                break

        # Extract date (CONFIDENCE: HIGH for standard formats)
        date_patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        parsed["date"] = date(
                            int(groups[0]), int(groups[1]), int(groups[2])
                        )
                    else:  # DD-MM-YYYY
                        parsed["date"] = date(
                            int(groups[2]), int(groups[1]), int(groups[0])
                        )
                    break
                except (ValueError, IndexError):
                    continue

        # Extract vet checks (CONFIDENCE: MEDIUM - format varies)
        vet_patterns = [
            r"(?:vet|veterinary).*?scratched.*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:was\s+)?scratched.*?vet",
        ]
        for pattern in vet_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                horse_name = match.group(1).strip()
                parsed["vet_checks"].append({
                    "horse": horse_name,
                    "reason": "vet check",
                    "confidence": 0.6,  # Medium confidence for regex extraction
                })

        # Extract track bias (CONFIDENCE: LOW - subjective language)
        bias_patterns = [
            r"track.*?(?:bias|favour(?:ing|ed)).*?([a-z\s]+)",
            r"(?:inside|outside|leaders|on-pace).*?advantag",
        ]
        for pattern in bias_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract surrounding context (50 chars)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                parsed["track_bias"] = text[start:end].strip()
                break

        # Extract rail position (CONFIDENCE: HIGH for standard formats)
        rail_patterns = [
            r"[Rr]ail.*?([+\-]?\d+m|[Tt]rue)",
            r"[Rr]ail\s+[Pp]osition.*?([+\-]?\d+m|[Tt]rue)",
        ]
        for pattern in rail_patterns:
            match = re.search(pattern, text)
            if match:
                parsed["rail_position"] = match.group(1).strip()
                break

        # Extract track condition (CONFIDENCE: HIGH)
        condition_patterns = [
            r"[Tt]rack\s+[Cc]ondition:?\s*([A-Za-z0-9\s]+)",
            r"going:?\s*([A-Za-z0-9\s]+)",
        ]
        for pattern in condition_patterns:
            match = re.search(pattern, text)
            if match:
                condition = match.group(1).strip()
                # Validate it looks like a track condition
                if re.match(r"^(Good|Heavy|Soft|Firm).*\d*$", condition, re.IGNORECASE):
                    parsed["track_condition"] = condition
                    break

        # Extract incidents (CONFIDENCE: MEDIUM)
        # Look for race-specific incidents
        incident_patterns = [
            r"[Rr]ace\s+(\d+).*?(fell|interference|checked|bumped|protest|inquiry)",
            r"(fell|interference|checked|bumped).*?[Rr]ace\s+(\d+)",
        ]
        for pattern in incident_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                incident_text = text[
                    max(0, match.start() - 50):min(len(text), match.end() + 100)
                ].strip()
                parsed["incidents"].append({
                    "description": incident_text,
                    "confidence": 0.5,  # Medium confidence
                })

        # Extract weather (CONFIDENCE: MEDIUM)
        weather_patterns = [
            r"[Ww]eather:?\s*([A-Za-z\s]+)",
            r"conditions:?\s*([A-Za-z\s]+)",
        ]
        for pattern in weather_patterns:
            match = re.search(pattern, text)
            if match:
                weather = match.group(1).strip()
                if len(weather) < 50:  # Sanity check
                    parsed["weather"] = weather
                    break

        return parsed

    def download_and_parse_report(
        self,
        venue: str,
        race_date: date | str,
        source: str = "rv",
    ) -> dict[str, Any]:
        """
        Download and parse a stewards report from online source.

        Args:
            venue: Venue code (e.g., 'flemington', 'randwick')
            race_date: Race date
            source: 'rv' (Racing Victoria) or 'rnsw' (Racing NSW)

        Returns:
            Parsed report data

        Note: This is a stub - actual implementation would require
        understanding each website's URL structure and scraping logic.
        For now, we focus on PDF parsing which is the core requirement.
        """
        if isinstance(race_date, str):
            race_date = date.fromisoformat(race_date)

        # TODO: Implement download logic for each source
        # This would require:
        # 1. Navigate to reports page
        # 2. Search/filter by venue and date
        # 3. Download PDF
        # 4. Parse with existing parse_pdf_report()

        raise NotImplementedError(
            "Online download not yet implemented. "
            "Use parse_pdf_report() with local PDF files."
        )

    def create_stewards_report_model(
        self, parsed_data: dict[str, Any], race_id: str
    ) -> list[StewardsReport]:
        """
        Convert parsed data to StewardsReport Pydantic models.

        Args:
            parsed_data: Data from parse_pdf_report()
            race_id: Race identifier

        Returns:
            List of StewardsReport models (one per incident/vet check)
        """
        reports = []

        # Create reports for vet checks
        for idx, vet_check in enumerate(parsed_data.get("vet_checks", [])):
            report = StewardsReport(
                steward_id=f"{race_id}-vet-{idx}",
                race_id=race_id,
                report_type=ReportType.GENERAL,
                report_text=f"Vet scratching: {vet_check['horse']}",
                incident_description=vet_check.get("reason", ""),
                horses_involved=[vet_check["horse"]],
                severity="low",
                scraped_at=datetime.now(),
            )
            reports.append(report)

        # Create reports for incidents
        for idx, incident in enumerate(parsed_data.get("incidents", [])):
            # Determine report type from description
            desc = incident["description"].lower()
            if "protest" in desc:
                report_type = ReportType.PROTEST
            elif "inquiry" in desc:
                report_type = ReportType.INQUIRY
            elif "fell" in desc or "fall" in desc:
                report_type = ReportType.FALL
            else:
                report_type = ReportType.GENERAL

            # Determine severity
            severity = "medium"
            if "fell" in desc or "protest" in desc:
                severity = "high"
            elif "checked" in desc or "bumped" in desc:
                severity = "low"

            report = StewardsReport(
                steward_id=f"{race_id}-incident-{idx}",
                race_id=race_id,
                report_type=report_type,
                report_text=incident["description"],
                incident_description=incident["description"],
                severity=severity,
                scraped_at=datetime.now(),
            )
            reports.append(report)

        return reports
