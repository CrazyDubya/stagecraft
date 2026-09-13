#!/usr/bin/env python3
"""CLI interface for Theater Critics Multi-Agent System.

Allows interactive scene analysis with rotating critic ensemble.
"""

import argparse
import asyncio
import json

from constants import (
    CLI_CRITICS_COUNT_RANGE,
    DEBUG_LOG_LEVEL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_ROTATING_CRITICS_COUNT,
    JSON_INDENT,
    MAX_ROTATING_CRITICS,
    MIN_ROTATING_CRITICS,
    SEPARATOR_LINE_LENGTH,
)
from logging_config import get_logger, setup_logging
from main import ConsensusAnalyzer, CriticEnsemble, SceneData, print_review_summary


class TheaterCriticsInterface:
    """Interactive CLI for theater critics system."""

    def __init__(self):
        """Initialize the CLI interface with critic ensemble."""
        self.ensemble = CriticEnsemble()

    def create_scene_interactive(self) -> SceneData:
        """Interactive scene creation."""
        print("\n🎭 CREATE NEW SCENE FOR ANALYSIS")
        print("=" * SEPARATOR_LINE_LENGTH)

        title = input("Scene Title: ").strip()
        musical = input("Musical Name: ").strip()
        description = input("Scene Description: ").strip()

        print("\nOptional Details (press Enter to skip):")
        lyrics = input("Lyrics: ").strip() or None
        stage_directions = input("Stage Directions: ").strip() or None
        character_notes = input("Character Notes: ").strip() or None

        return SceneData(
            title=title,
            musical=musical,
            description=description,
            lyrics=lyrics,
            stage_directions=stage_directions,
            character_notes=character_notes
        )

    def load_scene_from_file(self, filepath: str) -> SceneData:
        """Load scene from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return SceneData(**data)

    def save_scene_to_file(self, scene: SceneData, filepath: str):
        """Save scene to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(scene.__dict__, f, indent=JSON_INDENT)

    async def analyze_scene_async(self, scene: SceneData, num_critics: int = DEFAULT_ROTATING_CRITICS_COUNT):
        """Analyze scene with critic ensemble."""
        reviews = await self.ensemble.review_scene(scene, num_critics)
        consensus = ConsensusAnalyzer.calculate_consensus(reviews)
        print_review_summary(reviews, consensus)

    def list_critics(self):
        """List all available critics and their specialties."""
        print("\n🎭 AVAILABLE CRITICS")
        print("=" * SEPARATOR_LINE_LENGTH)
        for critic_type, critic in self.ensemble.critics.items():
            print(f"🎬 {critic.name}")
            print(f"   Type: {critic_type.value.title()}")
            print(f"   Model: {critic.model}")
            print(f"   Specialty: {critic.specialty}")
            print()


def create_sample_scenes():
    """Create sample scenes for testing."""
    samples = [
        {
            "title": "Defying Gravity",
            "musical": "Wicked",
            "description": "Elphaba's climactic moment of self-realization",
            "lyrics": "Something has changed within me...",
            "stage_directions": "Elphaba rises above the stage",
            "character_notes": "Transformation from outcast to empowered"
        },
        {
            "title": "Memory",
            "musical": "Cats",
            "description": "Grizabella's haunting solo",
            "lyrics": "Memory, all alone in the moonlight...",
            "stage_directions": "Spotlight on Grizabella center stage",
            "character_notes": "Longing for acceptance and past beauty"
        },
        {
            "title": "One Day More",
            "musical": "Les Misérables",
            "description": "Act I finale with full ensemble",
            "lyrics": "One day more, another day another destiny...",
            "stage_directions": "Multiple levels with full company",
            "character_notes": "Multiple character arcs converging"
        }
    ]

    for sample in samples:
        filename = f"sample_{sample['title'].lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(sample, f, indent=JSON_INDENT)
        print(f"Created {filename}")


async def main():
    """Main CLI function."""
    # Setup logging
    setup_logging(level=DEFAULT_LOG_LEVEL, log_file="theater_critics_cli.log")
    logger = get_logger()
    
    parser = argparse.ArgumentParser(description="Theater Critics Analysis System")
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Interactive mode for creating scenes"
    )
    parser.add_argument(
        "--file", "-f", type=str,
        help="Load scene from JSON file"
    )
    parser.add_argument(
        "--critics", "-c", type=int, default=DEFAULT_ROTATING_CRITICS_COUNT,
        help=f"Number of rotating critics ({MIN_ROTATING_CRITICS}-{MAX_ROTATING_CRITICS})"
    )
    parser.add_argument(
        "--save", "-s", type=str,
        help="Save scene to file after creation"
    )
    parser.add_argument(
        "--list-critics", "-l", action="store_true",
        help="List all available critics"
    )
    parser.add_argument(
        "--create-samples", action="store_true",
        help="Create sample scene files"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()
    
    if args.debug:
        setup_logging(level=DEBUG_LOG_LEVEL, log_file="theater_critics_cli_debug.log")
        logger = get_logger()
        logger.debug("Debug logging enabled")

    interface = TheaterCriticsInterface()

    if args.create_samples:
        logger.info("Creating sample scene files")
        create_sample_scenes()
        return

    if args.list_critics:
        logger.info("Listing available critics")
        interface.list_critics()
        return

    # Determine scene source
    if args.interactive:
        logger.info("Starting interactive scene creation")
        scene = interface.create_scene_interactive()
        if args.save:
            interface.save_scene_to_file(scene, args.save)
            logger.info(f"Scene saved to {args.save}")
    elif args.file:
        try:
            scene = interface.load_scene_from_file(args.file)
            logger.info(f"Loaded scene from {args.file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading file: {e}")
            return
    else:
        # Default: Use Defying Gravity sample
        logger.info("Using default Defying Gravity scene")
        scene = SceneData(
            title="Defying Gravity",
            musical="Wicked",
            description="Elphaba's climactic moment of self-realization and defiance",
            lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game""",
            stage_directions="Elphaba rises above the stage on a mechanical lift",
            character_notes="Transformation from outcast to empowered individual"
        )

    # Analyze the scene
    logger.info(f"Starting analysis with {args.critics} critics")
    await interface.analyze_scene_async(scene, args.critics)
    logger.info("Analysis complete")


if __name__ == "__main__":
    asyncio.run(main())
