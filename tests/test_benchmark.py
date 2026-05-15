"""Unit tests for benchmark module."""

import pytest
from unittest.mock import patch, MagicMock
from ollama_benchmark.benchmark import (
    generate_prompt,
    _compute_stats,
    SYSTEM_PROMPT,
    PROMPT_TEMPLATE,
)


class TestGeneratePrompt:
    """Tests for prompt generation logic."""

    def test_small_prompt(self):
        """Test generating a small prompt."""
        result = generate_prompt(64)
        assert len(result) > 0
        assert "software engineering problem" in result.lower()

    def test_medium_prompt(self):
        """Test generating a medium-sized prompt."""
        result = generate_prompt(1024)
        assert len(result) > 0
        assert "padding" in result.lower() or len(result.split()) > 100

    def test_large_prompt(self):
        """Test generating a large prompt."""
        result = generate_prompt(8192)
        assert len(result) > 0
        words = len(result.split())
        # Approximate check: ~8192 / 1.3 = ~6300 words expected
        assert words > 5000

    def test_prompt_contains_base_template(self):
        """Test that all prompts contain the base template."""
        for size in [64, 256, 1024, 4096]:
            result = generate_prompt(size)
            assert "I need help with a complex software engineering problem" in result


class TestComputeStats:
    """Tests for statistics computation."""

    def test_empty_list(self):
        """Test computing stats on empty list."""
        result = _compute_stats([])
        assert result["median"] == 0
        assert result["min"] == 0
        assert result["max"] == 0

    def test_single_value(self):
        """Test computing stats on single value."""
        result = _compute_stats([42.0])
        assert result["median"] == 42.0
        assert result["min"] == 42.0
        assert result["max"] == 42.0
        assert result["p95"] == 42.0
        assert result["p99"] == 42.0

    def test_multiple_values(self):
        """Test computing stats on multiple values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = _compute_stats(values)
        assert result["median"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0

    def test_median_calculation(self):
        """Test median calculation with even number of values."""
        values = [1.0, 2.0, 3.0, 4.0]
        result = _compute_stats(values)
        assert result["median"] == 2.5  # Average of 2 and 3

    def test_percentile_calculation(self):
        """Test percentile calculations."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        result = _compute_stats(values)
        assert result["p95"] >= 9.0
        assert result["p99"] >= 9.5


class TestSystemPrompt:
    """Tests for system prompt configuration."""

    def test_system_prompt_content(self):
        """Test that system prompt has expected content."""
        assert "expert coding assistant" in SYSTEM_PROMPT.lower()
        assert "clear" in SYSTEM_PROMPT.lower()
        assert "concise" in SYSTEM_PROMPT.lower()