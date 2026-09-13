#!/usr/bin/env python3
"""Theater Critics Multi-Agent System.

Uses Ollama models to provide rotating ensemble of theater critics for musical scene reviews.
"""

import asyncio
import json
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import httpx

from cache_system import cache_analysis_result
from constants import (
    CONSENSUS_MODERATE_THRESHOLD,
    CONSENSUS_SOME_THRESHOLD,
    CONSENSUS_STRONG_THRESHOLD,
    DEFAULT_LOG_LEVEL,
    DEFAULT_ROTATING_CRITICS_COUNT,
    EXAMPLE_AUDIENCE_ENGAGEMENT,
    EXAMPLE_MUSICAL_COMPOSITION,
    EXAMPLE_NARRATIVE_INTEGRATION,
    EXAMPLE_OVERALL_SCORE,
    EXAMPLE_PERFORMANCE_QUALITY,
    EXAMPLE_PRODUCTION_ELEMENTS,
    EXAMPLE_SPECIALTY_SCORE,
    HTTP_TIMEOUT_SECONDS,
    JSON_INDENT,
    OLLAMA_GENERATE_ENDPOINT,
    SCORE_DEFAULT_FALLBACK,
    SCORE_DEFAULT_SPECIALTY,
    SCORE_ERROR_FALLBACK,
    SCORE_MAX,
    SCORE_MIN,
    SECTION_LINE_LENGTH,
    SEPARATOR_LINE_LENGTH,
    SUBSECTION_LINE_LENGTH,
    TEXT_TRUNCATION_LENGTH,
)
from logging_config import get_logger, log_performance, setup_logging


class CriticType(Enum):
    """Enumeration of different critic specializations."""

    PRIMARY = "primary"
    ACADEMIC = "academic"
    POPULAR = "popular"
    EXPERIMENTAL = "experimental"
    COMMERCIAL = "commercial"
    EMOTION = "emotion"


@dataclass
class SceneData:
    """Data structure for musical theater scene information."""

    title: str
    musical: str
    description: str
    lyrics: Optional[str] = None
    stage_directions: Optional[str] = None
    character_notes: Optional[str] = None


@dataclass
class ReviewScore:
    """Scoring structure for different aspects of theatrical analysis."""

    overall: float  # SCORE_MIN-SCORE_MAX
    musical_composition: float
    performance_quality: float
    production_elements: float
    narrative_integration: float
    audience_engagement: float
    specialty_score: float  # Critic's specialty focus


@dataclass
class CriticReview:
    """Complete review from a single critic including scores and analysis."""

    critic_name: str
    critic_type: CriticType
    model_used: str
    review_text: str
    scores: ReviewScore
    key_strengths: List[str]
    areas_for_improvement: List[str]
    specialty_analysis: str


class TheaterCritic:
    """Base class for theater critics using different Ollama models."""

    def __init__(self, name: str, critic_type: CriticType, model: str, specialty: str):
        """Initialize a theater critic with specific model and expertise.

        Args:
            name: Human-readable name of the critic
            critic_type: Type of critical specialization
            model: Ollama model identifier to use
            specialty: Area of expertise description
        """
        self.name = name
        self.critic_type = critic_type
        self.model = model
        self.specialty = specialty
        self.ollama_url = OLLAMA_GENERATE_ENDPOINT

    @log_performance
    async def analyze_scene(self, scene: SceneData) -> CriticReview:
        """Analyze a musical theater scene from this critic's perspective."""
        logger = get_logger()
        logger.info(f"Starting analysis for scene: {scene.title} from {scene.musical}")
        
        prompt = self._build_analysis_prompt(scene)

        try:
            response = await self._query_ollama(prompt)
            result = self._parse_response(response, scene)
            logger.info(f"Successfully analyzed scene: {scene.title} with score {result.scores.overall}")
            return result
        except Exception as e:
            logger.error(f"Analysis failed for scene {scene.title}: {str(e)}")
            return self._create_error_review(str(e))

    def _build_analysis_prompt(self, scene: SceneData) -> str:
        """Build specialized prompt for this critic type."""
        base_prompt = f"""
You are {self.name}, a renowned theater critic specializing in {self.specialty}.

Analyze this musical theater scene:

**Musical:** {scene.musical}
**Scene:** {scene.title}
**Description:** {scene.description}
"""

        if scene.lyrics:
            base_prompt += f"\n**Lyrics:**\n{scene.lyrics}\n"
        if scene.stage_directions:
            base_prompt += f"\n**Stage Directions:**\n{scene.stage_directions}\n"
        if scene.character_notes:
            base_prompt += f"\n**Character Notes:**\n{scene.character_notes}\n"

        specialty_prompt = self._get_specialty_prompt()

        scoring_prompt = f"""
Provide your analysis in this JSON format:
{{
    "review_text": "Your comprehensive review (2-3 paragraphs)",
    "scores": {{
        "overall": {EXAMPLE_OVERALL_SCORE},
        "musical_composition": {EXAMPLE_MUSICAL_COMPOSITION},
        "performance_quality": {EXAMPLE_PERFORMANCE_QUALITY},
        "production_elements": {EXAMPLE_PRODUCTION_ELEMENTS},
        "narrative_integration": {EXAMPLE_NARRATIVE_INTEGRATION},
        "audience_engagement": {EXAMPLE_AUDIENCE_ENGAGEMENT},
        "specialty_score": {EXAMPLE_SPECIALTY_SCORE}
    }},
    "key_strengths": ["strength 1", "strength 2", "strength 3"],
    "areas_for_improvement": ["improvement 1", "improvement 2"],
    "specialty_analysis": "Your focused analysis on your specialty area"
}}

All scores should be between {SCORE_MIN} and {SCORE_MAX}. Be critical but fair.
"""

        return base_prompt + specialty_prompt + scoring_prompt

    def _get_specialty_prompt(self) -> str:
        """Get specialized analysis prompt based on critic type."""
        prompts = {
            CriticType.PRIMARY: """
As the lead critic, provide a comprehensive analysis covering all aspects of the scene.
Focus on overall artistic merit, technical execution, and cultural significance.
""",
            CriticType.ACADEMIC: """
Focus on musical theory, composition techniques, historical context, and artistic innovation.
Analyze harmony, melody, lyrical sophistication, and connections to musical theater traditions.
""",
            CriticType.POPULAR: """
Evaluate audience appeal, entertainment value, and mainstream accessibility.
Consider singability, memorability, emotional connection, and commercial potential.
""",
            CriticType.EXPERIMENTAL: """
Assess artistic risk-taking, innovation, and avant-garde elements.
Look for experimental staging, unconventional musical structures, and boundary-pushing concepts.
""",
            CriticType.COMMERCIAL: """
Analyze production value, marketability, and mainstream appeal.
Consider budget implications, touring potential, and broad audience accessibility.
""",
            CriticType.EMOTION: """
Focus on emotional impact, character development, and storytelling effectiveness.
Evaluate how well the scene conveys emotion and advances character arcs.
""",
        }
        return prompts.get(self.critic_type, prompts[CriticType.PRIMARY])

    async def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response."""
        logger = get_logger()
        logger.debug(f"Querying Ollama model: {self.model}")
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    self.ollama_url,
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                result = response.json()["response"]
                logger.debug(f"Received response from {self.model}: {len(result)} characters")
                return result
        except httpx.TimeoutException:
            logger.error(f"Timeout waiting for {self.model}")
            raise Exception(f"Timeout waiting for {self.model}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} from {self.model}: {e.response.text}")
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to query {self.model}: {str(e)}")
            raise Exception(f"Failed to query {self.model}: {str(e)}")

    def _parse_response(self, response: str, scene: SceneData) -> CriticReview:
        """Parse Ollama response into CriticReview object."""
        logger = get_logger()
        
        try:
            # Try to extract JSON from response if it contains other text
            response = response.strip()

            # Look for JSON block in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                logger.debug(f"Successfully parsed JSON response from {self.name}")
            else:
                # If no JSON found, create fallback review
                logger.warning(f"No JSON found in response from {self.name}, using fallback")
                return self._create_fallback_review(response)

            scores = ReviewScore(
                overall=data["scores"]["overall"],
                musical_composition=data["scores"]["musical_composition"],
                performance_quality=data["scores"]["performance_quality"],
                production_elements=data["scores"]["production_elements"],
                narrative_integration=data["scores"]["narrative_integration"],
                audience_engagement=data["scores"]["audience_engagement"],
                specialty_score=data["scores"]["specialty_score"],
            )

            return CriticReview(
                critic_name=self.name,
                critic_type=self.critic_type,
                model_used=self.model,
                review_text=data["review_text"],
                scores=scores,
                key_strengths=data["key_strengths"],
                areas_for_improvement=data["areas_for_improvement"],
                specialty_analysis=data["specialty_analysis"],
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse JSON response from {self.name}: {str(e)}")
            return self._create_fallback_review(response)

    def _create_fallback_review(self, response: str) -> CriticReview:
        """Create fallback review from non-JSON response."""
        # Extract basic analysis from text response
        review_text = response[:TEXT_TRUNCATION_LENGTH] + "..." if len(response) > TEXT_TRUNCATION_LENGTH else response

        # Assign moderate scores as fallback
        scores = ReviewScore(
            overall=SCORE_DEFAULT_FALLBACK,
            musical_composition=SCORE_DEFAULT_FALLBACK,
            performance_quality=SCORE_DEFAULT_FALLBACK,
            production_elements=SCORE_DEFAULT_FALLBACK,
            narrative_integration=SCORE_DEFAULT_FALLBACK,
            audience_engagement=SCORE_DEFAULT_FALLBACK,
            specialty_score=SCORE_DEFAULT_SPECIALTY,
        )

        return CriticReview(
            critic_name=self.name,
            critic_type=self.critic_type,
            model_used=self.model,
            review_text=review_text,
            scores=scores,
            key_strengths=["Analysis provided in narrative form"],
            areas_for_improvement=["Structured scoring format needed"],
            specialty_analysis=f"Free-form analysis from {self.specialty} perspective",
        )

    def _create_error_review(self, error_msg: str) -> CriticReview:
        """Create error review when analysis fails."""
        return CriticReview(
            critic_name=self.name,
            critic_type=self.critic_type,
            model_used=self.model,
            review_text=f"Analysis failed: {error_msg}",
            scores=ReviewScore(
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK, 
                SCORE_ERROR_FALLBACK
            ),
            key_strengths=["Unable to analyze"],
            areas_for_improvement=["System error occurred"],
            specialty_analysis="Analysis unavailable due to error",
        )


class CriticEnsemble:
    """Manages the rotating ensemble of theater critics."""

    def __init__(self):
        """Initialize the critic ensemble with all available critics."""
        self.critics = self._initialize_critics()
        self.primary_critic = self.critics[CriticType.PRIMARY]

    def _initialize_critics(self) -> Dict[CriticType, TheaterCritic]:
        """Initialize all critic agents with their specialized models."""
        return {
            CriticType.PRIMARY: TheaterCritic(
                "Eleanor Hartwell",
                CriticType.PRIMARY,
                "gemma2:9b",
                "comprehensive theatrical analysis",
            ),
            CriticType.ACADEMIC: TheaterCritic(
                "Dr. Marcus Steinberg",
                CriticType.ACADEMIC,
                "qwen2.5:3b",
                "musical theory and historical context",
            ),
            CriticType.POPULAR: TheaterCritic(
                "Casey Rodriguez",
                CriticType.POPULAR,
                "llama3.2:3b",
                "audience appeal and entertainment value",
            ),
            CriticType.EXPERIMENTAL: TheaterCritic(
                "Zara Blackthorne",
                CriticType.EXPERIMENTAL,
                "theater-long-context:latest",
                "artistic innovation and experimental theater",
            ),
            CriticType.COMMERCIAL: TheaterCritic(
                "Robert Sterling",
                CriticType.COMMERCIAL,
                "llama3:8b",
                "production value and commercial viability",
            ),
            CriticType.EMOTION: TheaterCritic(
                "Luna Chen",
                CriticType.EMOTION,
                "gemma:7b",
                "emotional impact and character development",
            ),
        }

    def select_rotating_critics(self, count: int = DEFAULT_ROTATING_CRITICS_COUNT) -> List[TheaterCritic]:
        """Select random subset of secondary critics for this review."""
        secondary_critics = [
            critic
            for critic_type, critic in self.critics.items()
            if critic_type != CriticType.PRIMARY
        ]
        return random.sample(secondary_critics, min(count, len(secondary_critics)))

    @log_performance
    async def review_scene(
        self, scene: SceneData, num_rotating_critics: int = DEFAULT_ROTATING_CRITICS_COUNT
    ) -> List[CriticReview]:
        """Get reviews from primary critic and rotating ensemble."""
        logger = get_logger()
        logger.info(f"Starting ensemble analysis for scene: {scene.title} from {scene.musical}")
        logger.info(f"Primary critic: {self.primary_critic.name}")

        # Always include primary critic
        reviews = []

        # Get rotating critics
        rotating_critics = self.select_rotating_critics(num_rotating_critics)
        critic_names = [c.name for c in rotating_critics]
        logger.info(f"Selected rotating critics: {', '.join(critic_names)}")

        # Run all analyses concurrently
        all_critics = [self.primary_critic] + rotating_critics
        tasks = [critic.analyze_scene(scene) for critic in all_critics]

        logger.info("Starting concurrent critic analyses...")
        reviews = await asyncio.gather(*tasks)
        
        logger.info(f"Completed ensemble analysis with {len(reviews)} reviews")
        return reviews


class ConsensusAnalyzer:
    """Analyzes consensus and disagreements between critics."""

    @staticmethod
    def calculate_consensus(reviews: List[CriticReview]) -> Dict:
        """Calculate consensus scores and identify agreements/disagreements."""
        if not reviews:
            return {}

        # Calculate average scores
        avg_scores = {}
        score_fields = [
            "overall",
            "musical_composition",
            "performance_quality",
            "production_elements",
            "narrative_integration",
            "audience_engagement",
        ]

        for field in score_fields:
            scores = [getattr(review.scores, field) for review in reviews]
            avg_scores[field] = sum(scores) / len(scores)

        # Find score variations
        score_variations = {}
        for field in score_fields:
            scores = [getattr(review.scores, field) for review in reviews]
            score_variations[field] = max(scores) - min(scores)

        # Identify consensus level
        overall_variation = score_variations["overall"]
        if overall_variation <= CONSENSUS_STRONG_THRESHOLD:
            consensus_level = "Strong Agreement"
        elif overall_variation <= CONSENSUS_MODERATE_THRESHOLD:
            consensus_level = "Moderate Agreement"
        elif overall_variation <= CONSENSUS_SOME_THRESHOLD:
            consensus_level = "Some Disagreement"
        else:
            consensus_level = "Significant Disagreement"

        # Find common themes in strengths and improvements
        all_strengths = []
        all_improvements = []
        for review in reviews:
            all_strengths.extend(review.key_strengths)
            all_improvements.extend(review.areas_for_improvement)

        return {
            "consensus_level": consensus_level,
            "average_scores": avg_scores,
            "score_variations": score_variations,
            "common_strengths": list(set(all_strengths)),
            "common_improvements": list(set(all_improvements)),
            "critic_count": len(reviews),
        }


def print_review_summary(reviews: List[CriticReview], consensus: Dict):
    """Print formatted review summary."""
    print("\n" + "=" * SEPARATOR_LINE_LENGTH)
    print("🎭 THEATER CRITICS ENSEMBLE REVIEW")
    print("=" * SEPARATOR_LINE_LENGTH)

    # Consensus overview
    print(f"\n📊 CONSENSUS: {consensus['consensus_level']}")
    print(f"Overall Score: {consensus['average_scores']['overall']:.1f}/{SCORE_MAX}")
    print(f"Critics Participating: {consensus['critic_count']}")

    # Individual reviews
    print("\n" + "-" * SECTION_LINE_LENGTH)
    print("INDIVIDUAL CRITIC REVIEWS")
    print("-" * SECTION_LINE_LENGTH)

    for review in reviews:
        print(f"\n🎬 {review.critic_name} ({review.critic_type.value.title()})")
        print(f"Model: {review.model_used}")
        print(f"Overall Score: {review.scores.overall}/{SCORE_MAX}")
        print(f"Specialty Score: {review.scores.specialty_score}/{SCORE_MAX}")
        print(f"\nReview: {review.review_text}")
        print(f"\nStrengths: {', '.join(review.key_strengths)}")
        print(f"Improvements: {', '.join(review.areas_for_improvement)}")
        print(f"\nSpecialty Analysis: {review.specialty_analysis}")
        print("-" * SUBSECTION_LINE_LENGTH)

    # Detailed scores
    print("\n📈 DETAILED CONSENSUS SCORES")
    print("-" * SUBSECTION_LINE_LENGTH)
    for category, score in consensus["average_scores"].items():
        variation = consensus["score_variations"][category]
        print(
            f"{category.replace('_', ' ').title()}: {score:.1f}/{SCORE_MAX} (±{variation:.1f})"
        )


async def main():
    """Example usage of the theater critics system."""
    # Setup logging
    setup_logging(level=DEFAULT_LOG_LEVEL, log_file="theater_critics.log")
    logger = get_logger()
    logger.info("Starting Theater Critics System")
    
    # Create sample scene
    scene = SceneData(
        title="Defying Gravity",
        musical="Wicked",
        description="Elphaba's climactic moment of self-realization and defiance at the end of Act I",
        lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game

Too late for second-guessing
Too late to go back to sleep
It's time to trust my instincts
Close my eyes and leap!""",
        stage_directions="Elphaba rises above the stage on a mechanical lift, cape billowing, as the ensemble looks up in awe and fear",
        character_notes="Elphaba transforms from outcast to empowered individual, accepting her differences as strengths",
    )

    # Initialize critic ensemble
    ensemble = CriticEnsemble()

    # Get reviews
    reviews = await ensemble.review_scene(scene)

    # Calculate consensus
    consensus = ConsensusAnalyzer.calculate_consensus(reviews)

    # Print results
    print_review_summary(reviews, consensus)
    
    logger.info("Theater Critics System analysis complete")


if __name__ == "__main__":
    asyncio.run(main())
