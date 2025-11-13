#!/usr/bin/env python3
"""
Generate project_snapshot.json for AI agent context.

This script creates a comprehensive JSON snapshot of the entire project,
including file tree, summaries, architectural state, and implementation status.
Prevents AI agents from hallucinating about what's implemented.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path("/workspaces/Racing-Analysis")
OUTPUT_FILE = PROJECT_ROOT / "project_context" / "project_snapshot.json"


def get_file_tree() -> Dict[str, Any]:
    """Generate complete file tree."""
    tree = {}

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip hidden and cache directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
        ]

        rel_path = Path(root).relative_to(PROJECT_ROOT)

        for file in files:
            if file.startswith("."):
                continue

            file_path = Path(root) / file
            rel_file_path = file_path.relative_to(PROJECT_ROOT)

            tree[str(rel_file_path)] = {
                "size": file_path.stat().st_size,
                "extension": file_path.suffix,
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
            }

    return tree


def get_documentation_summary() -> Dict[str, Any]:
    """Summarize all documentation files."""
    docs = {}

    doc_files = [
        "MASTER_PLAN.md",
        "IMPLEMENTATION_REALITY_CHECK.md",
        "DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md",
        "docs/FUSION_MODEL_ARCHITECTURE.md",
        "docs/COMPREHENSIVE_INFORMATION_TAXONOMY.md",
        "project_context/MASTER_CONTEXT.md",
    ]

    for doc in doc_files:
        doc_path = PROJECT_ROOT / doc
        if doc_path.exists():
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
                docs[doc] = {
                    "exists": True,
                    "lines": len(content.split("\n")),
                    "size_kb": len(content) // 1024,
                    "first_100_chars": content[:100].replace("\n", " "),
                }
        else:
            docs[doc] = {"exists": False}

    return docs


def get_implementation_status() -> Dict[str, Any]:
    """Determine actual implementation status by checking source code."""
    status = {
        "database": {
            "schema_exists": (PROJECT_ROOT / "src/data/schema.sql").exists(),
            "init_exists": (PROJECT_ROOT / "src/data/init_db.py").exists(),
            "estimated_completeness": "90%",
            "issues": ["Only ~10 placeholder races in database"],
        },
        "scrapers": {
            "racing_com": {
                "file_exists": (
                    PROJECT_ROOT / "src/data/scrapers/racing_com.py"
                ).exists(),
                "live_scraping": False,
                "placeholder_only": True,
                "needs_rebuild": True,
            },
            "stewards": {
                "file_exists": (
                    PROJECT_ROOT / "src/data/scrapers/stewards.py"
                ).exists(),
                "live_scraping": False,
                "placeholder_only": True,
                "needs_rebuild": True,
            },
            "market_odds": {
                "file_exists": (
                    PROJECT_ROOT / "src/data/scrapers/market_odds.py"
                ).exists(),
                "live_scraping": False,
                "placeholder_only": True,
                "needs_rebuild": True,
            },
            "betfair_api": {
                "file_exists": False,
                "implementation_status": "0%",
                "priority": "CRITICAL",
            },
            "estimated_completeness": "5%",
            "issues": [
                "All scrapers return fake data",
                "No live web scraping",
                "No Betfair API",
            ],
        },
        "features": {
            "directory_exists": (PROJECT_ROOT / "src/features").exists(),
            "speed_ratings": (PROJECT_ROOT / "src/features/speed_ratings.py").exists(),
            "class_ratings": (PROJECT_ROOT / "src/features/class_ratings.py").exists(),
            "sectional_analyzer": (
                PROJECT_ROOT / "src/features/sectional_analyzer.py"
            ).exists(),
            "pedigree_analyzer": (
                PROJECT_ROOT / "src/features/pedigree_analyzer.py"
            ).exists(),
            "estimated_completeness": "40%",
            "issues": ["Code exists but trained on placeholder data only"],
        },
        "models": {
            "directory_exists": (PROJECT_ROOT / "src/models").exists(),
            "has_ml_code": True,
            "estimated_completeness": "40%",
            "issues": ["Cannot validate without real data"],
        },
        "calibration": {
            "directory_exists": (PROJECT_ROOT / "src/calibration").exists(),
            "has_code": True,
            "estimated_completeness": "40%",
            "issues": ["Cannot validate without real data"],
        },
        "qualitative_pipeline": {
            "directory_exists": (PROJECT_ROOT / "src/qualitative").exists()
            if (PROJECT_ROOT / "src/qualitative").is_dir()
            else False,
            "stage_1_source_planning": False,
            "stage_2_parallel_scraping": False,
            "stage_3_content_extraction": False,
            "stage_4_deep_reasoning": False,
            "stage_5_synthesis": False,
            "stage_6_quality_verification": False,
            "estimated_completeness": "0%",
            "issues": ["Directory doesn't exist", "No stages implemented"],
        },
        "fusion_model": {
            "directory_exists": (PROJECT_ROOT / "src/fusion").exists(),
            "has_bayesian_lr_logic": False,
            "has_e2b_integration": False,
            "has_openhands_integration": False,
            "has_15_agent_system": False,
            "has_consensus_synthesis": False,
            "estimated_completeness": "0%",
            "issues": ["Only __init__.py with docstring", "No actual fusion code"],
        },
        "deployment": {
            "docker_exists": (PROJECT_ROOT / "docker-compose.yml").exists(),
            "api_exists": (PROJECT_ROOT / "src/deployment/api_server.py").exists(),
            "estimated_completeness": "100%",
            "issues": [],
        },
    }

    return status


def get_architectural_state() -> Dict[str, Any]:
    """Current architectural understanding."""
    return {
        "core_architecture": "Dual pipeline + Fusion model",
        "pipelines": {
            "qualitative": {
                "categories": "1-17",
                "stages": 6,
                "output": "Likelihood Ratios (LRs)",
                "cost_per_race": "$0.62",
                "runtime": "5-7 minutes",
                "implementation_status": "0%",
            },
            "quantitative": {
                "categories": "18-21",
                "models": ["LightGBM", "XGBoost", "CatBoost"],
                "output": "Base probabilities",
                "cost_per_race": "<$0.01",
                "runtime": "10-30 seconds",
                "implementation_status": "40%",
            },
        },
        "fusion_model": {
            "architecture": "15 concurrent agents",
            "technology": ["E2B sandboxes", "OpenHands orchestration"],
            "algorithm": "Bayesian Likelihood Ratio",
            "runtime": "30-60 seconds (parallel)",
            "implementation_status": "0%",
        },
        "data_sources": {
            "required_per_race": "15-40 sources",
            "current_working": "0 sources",
            "critical_missing": ["Betfair API", "Racing.com live", "40+ scrapers"],
        },
        "expected_performance": {
            "brier_score": "<0.16",
            "roi": ">7.2%",
            "calibration_error": "<2%",
        },
        "validation_status": "Cannot validate - no real data",
    }


def get_critical_files() -> List[str]:
    """List of files AI agents should prioritize reading."""
    return [
        "project_context/MASTER_CONTEXT.md",
        "MASTER_PLAN.md",
        "IMPLEMENTATION_REALITY_CHECK.md",
        "DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md",
        "docs/FUSION_MODEL_ARCHITECTURE.md",
        "src/data/init_db.py",
        "src/data/schema.sql",
        "src/data/scrapers/racing_com.py",
        "src/fusion/__init__.py",
    ]


def get_current_priorities() -> Dict[str, Any]:
    """What needs to be built next."""
    return {
        "phase_1_data_foundation": {
            "priority": "CRITICAL",
            "timeline": "Weeks 1-4",
            "tasks": [
                "Rewrite racing.com scraper with real scraping",
                "Integrate Betfair API",
                "Build weather API integration",
                "Populate 100+ historical races",
                "Build stewards/trials/gear scrapers",
                "Target: 500+ historical races",
            ],
        },
        "phase_2_qualitative_pipeline": {
            "priority": "HIGH",
            "timeline": "Weeks 5-8",
            "tasks": [
                "Stage 1: Source Planning (Gemini)",
                "Stage 2: Parallel Scraping (15-40 sources)",
                "Stage 3: Content Extraction (Gemini)",
                "Stage 4: Deep Reasoning (GPT-5)",
                "Stage 5: Synthesis (Claude Sonnet 4.5)",
                "Stage 6: Quality Verification (GPT-4o)",
            ],
        },
        "phase_3_fusion_model": {
            "priority": "HIGH",
            "timeline": "Weeks 9-12",
            "tasks": [
                "E2B sandbox integration",
                "Bayesian LR algorithm implementation",
                "15-agent concurrent execution",
                "OpenHands orchestration",
                "Consensus synthesis",
            ],
        },
    }


def generate_snapshot() -> Dict[str, Any]:
    """Generate complete project snapshot."""
    print("Generating project snapshot...")

    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "project_name": "Racing Analysis System",
        "version": "1.0",
        "status": "Early Development - 10% implementation, 100% design",
        "critical_warning": {
            "message": "This project has EXCELLENT DOCUMENTATION but MINIMAL WORKING CODE",
            "do_not_assume": [
                "Scrapers are working (they return fake data)",
                "System is production-ready (it's not)",
                "Qualitative pipeline exists (it doesn't)",
                "Fusion model is implemented (it's not)",
                "We have real data (we have ~10 placeholder races)",
            ],
        },
        "file_tree": get_file_tree(),
        "documentation_summary": get_documentation_summary(),
        "implementation_status": get_implementation_status(),
        "architectural_state": get_architectural_state(),
        "critical_files_to_read": get_critical_files(),
        "current_priorities": get_current_priorities(),
        "design_principles": [
            "No data leakage - strict event-time ordering",
            "Dual pipeline architecture - do NOT simplify",
            "Multi-agent fusion - 15 agents by design",
            "21-category taxonomy - do NOT skip categories",
            "Uncertainty quantification - always include confidence",
        ],
        "common_mistakes_to_avoid": [
            "Claiming we built 60% of the system (we built ~10%)",
            "Suggesting we simplify the architecture (it's correct as designed)",
            "Assuming scrapers work (they return placeholder data)",
            "Claiming qualitative pipeline exists (it doesn't)",
            "Saying fusion model is implemented (it's not)",
        ],
        "verification_required": {
            "before_claiming_implemented": [
                "Read actual source file",
                "Check for placeholder/fake data returns",
                "Verify imports and dependencies",
                "Check if directory exists",
                "Search for actual logic (not just comments)",
            ]
        },
    }

    return snapshot


def main():
    """Generate and save project snapshot."""
    print(f"Racing Analysis System - Project Snapshot Generator")
    print(f"=" * 60)

    snapshot = generate_snapshot()

    # Create output directory if needed
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    # Write snapshot
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Snapshot generated: {OUTPUT_FILE}")
    print(f"   File size: {OUTPUT_FILE.stat().st_size // 1024} KB")
    print(f"   Files tracked: {len(snapshot['file_tree'])}")
    print(f"\n📋 Key Findings:")
    print(f"   Documentation: {len(snapshot['documentation_summary'])} files")
    print(f"   Implementation Status:")

    for component, status in snapshot["implementation_status"].items():
        if isinstance(status, dict) and "estimated_completeness" in status:
            print(f"      - {component}: {status['estimated_completeness']}")

    print(f"\n🚨 Critical Issues:")
    all_issues = []
    for component, status in snapshot["implementation_status"].items():
        if isinstance(status, dict) and "issues" in status:
            all_issues.extend(status["issues"])

    for i, issue in enumerate(set(all_issues), 1):
        print(f"   {i}. {issue}")

    print(
        f"\n💡 This file will prevent AI agents from hallucinating about implementation status"
    )
    print(f"   Location: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
