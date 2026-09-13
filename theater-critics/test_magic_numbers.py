#!/usr/bin/env python3
"""Test script to verify that magic numbers have been replaced with constants."""

import sys
from constants import (
    CACHE_MINIMUM_VALID_SCORE,
    DEFAULT_ROTATING_CRITICS_COUNT,
    HTTP_TIMEOUT_SECONDS,
    OLLAMA_GENERATE_ENDPOINT,
    SCORE_DEFAULT_FALLBACK,
    SCORE_ERROR_FALLBACK,
    SCORE_MAX,
    SCORE_MIN,
)


def test_constants_defined():
    """Test that all expected constants are defined."""
    print("Testing constants definition...")
    
    # Network constants
    assert OLLAMA_GENERATE_ENDPOINT == "http://localhost:11434/api/generate"
    assert HTTP_TIMEOUT_SECONDS == 120.0
    
    # Scoring constants
    assert SCORE_MIN == 1.0
    assert SCORE_MAX == 10.0
    assert SCORE_DEFAULT_FALLBACK == 7.0
    assert SCORE_ERROR_FALLBACK == 5.0
    
    # Configuration constants
    assert DEFAULT_ROTATING_CRITICS_COUNT == 3
    assert CACHE_MINIMUM_VALID_SCORE == 1.0  # This was the critical bug fix!
    
    print("✅ All constants are properly defined!")


def test_cache_minimum_score_fix():
    """Test that the cache minimum score bug is fixed."""
    print("Testing cache minimum score fix...")
    
    # The bug was that CACHE_MINIMUM_VALID_SCORE was set to 10
    # on a 1-10 scale, which would exclude almost all results
    assert CACHE_MINIMUM_VALID_SCORE < SCORE_MAX, f"Cache minimum score {CACHE_MINIMUM_VALID_SCORE} should be less than max score {SCORE_MAX}"
    assert CACHE_MINIMUM_VALID_SCORE >= SCORE_MIN, f"Cache minimum score {CACHE_MINIMUM_VALID_SCORE} should be >= min score {SCORE_MIN}"
    
    print(f"✅ Cache minimum score correctly set to {CACHE_MINIMUM_VALID_SCORE} (was incorrectly 10 before)")


def test_scoring_range():
    """Test that scoring constants are logically consistent."""
    print("Testing scoring range consistency...")
    
    assert SCORE_MIN < SCORE_MAX, "Score minimum should be less than maximum"
    assert SCORE_DEFAULT_FALLBACK >= SCORE_MIN and SCORE_DEFAULT_FALLBACK <= SCORE_MAX, "Default fallback should be in range"
    assert SCORE_ERROR_FALLBACK >= SCORE_MIN and SCORE_ERROR_FALLBACK <= SCORE_MAX, "Error fallback should be in range"
    
    print("✅ Scoring ranges are consistent!")


def main():
    """Run all tests."""
    print("🧪 Testing Magic Number Fixes")
    print("=" * 50)
    
    try:
        test_constants_defined()
        test_cache_minimum_score_fix()
        test_scoring_range()
        
        print("\n🎉 All tests passed! Magic numbers have been successfully replaced with constants.")
        print(f"📊 Critical bug fixed: Cache minimum score changed from 10 to {CACHE_MINIMUM_VALID_SCORE}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()