"""Configuration constants for Theater Critics System.

This module contains all configurable constants used throughout the system,
replacing magic numbers with named constants for better maintainability.
"""

# Network Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
HTTP_TIMEOUT_SECONDS = 120.0

# Scoring System Constants
SCORE_MIN = 1.0
SCORE_MAX = 10.0
SCORE_DEFAULT_FALLBACK = 7.0
SCORE_DEFAULT_SPECIALTY = 7.5
SCORE_ERROR_FALLBACK = 5.0

# Consensus Analysis Thresholds
CONSENSUS_STRONG_THRESHOLD = 1.0      # <= 1.0 variation = Strong Agreement
CONSENSUS_MODERATE_THRESHOLD = 2.0    # <= 2.0 variation = Moderate Agreement  
CONSENSUS_SOME_THRESHOLD = 3.0        # <= 3.0 variation = Some Disagreement
# > 3.0 variation = Significant Disagreement

# Critic Ensemble Configuration
DEFAULT_ROTATING_CRITICS_COUNT = 3
MIN_ROTATING_CRITICS = 1
MAX_ROTATING_CRITICS = 5

# Cache Configuration
DEFAULT_CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_HASH_DIGEST_SIZE = 16       # Blake2b digest size in bytes
CACHE_MINIMUM_VALID_SCORE = 1.0   # Minimum score to cache (1-10 scale)

# Text Processing Limits
TEXT_TRUNCATION_LENGTH = 500
CONTEXT_DISPLAY_LENGTH = 80
CONTEXT_SIZE_DEFAULT = 50

# Logging Configuration
DEFAULT_LOG_LEVEL = "INFO"
DEBUG_LOG_LEVEL = "DEBUG"

# CLI Configuration
CLI_CRITICS_COUNT_RANGE = (MIN_ROTATING_CRITICS, MAX_ROTATING_CRITICS)

# File Extensions
CACHE_FILE_EXTENSION = ".cache"
JSON_FILE_EXTENSION = ".json"
LOG_FILE_EXTENSION = ".log"

# Display Constants
SEPARATOR_LINE_LENGTH = 80
SECTION_LINE_LENGTH = 60
SUBSECTION_LINE_LENGTH = 40
JSON_INDENT = 2

# Example Scoring (used in prompts)
EXAMPLE_OVERALL_SCORE = 7.5
EXAMPLE_MUSICAL_COMPOSITION = 8.0
EXAMPLE_PERFORMANCE_QUALITY = 7.0
EXAMPLE_PRODUCTION_ELEMENTS = 8.5
EXAMPLE_NARRATIVE_INTEGRATION = 6.5
EXAMPLE_AUDIENCE_ENGAGEMENT = 7.8
EXAMPLE_SPECIALTY_SCORE = 8.2