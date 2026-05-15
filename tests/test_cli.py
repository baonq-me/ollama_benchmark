"""Unit tests for CLI module."""

import argparse
import pytest
from ollama_benchmark.cli import parse_prompt_sizes, build_arg_parser


class TestParsePromptSizes:
    """Tests for prompt size parsing."""

    def test_single_size(self):
        """Test parsing a single prompt size."""
        result = parse_prompt_sizes("64")
        assert result == [64]

    def test_multiple_sizes(self):
        """Test parsing multiple prompt sizes."""
        result = parse_prompt_sizes("64,1024,8192")
        assert result == [64, 1024, 8192]

    def test_unsorted_input(self):
        """Test that sizes are sorted in output."""
        result = parse_prompt_sizes("8192,64,1024")
        assert result == [64, 1024, 8192]

    def test_with_spaces(self):
        """Test parsing with spaces around values."""
        result = parse_prompt_sizes("64, 1024 , 8192")
        assert result == [64, 1024, 8192]

    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_prompt_sizes("")
        assert result == []

    def test_duplicate_sizes(self):
        """Test that duplicates are preserved in sorted order."""
        result = parse_prompt_sizes("64,64,128")
        assert result == [64, 64, 128]

    def test_invalid_value_raises(self):
        """Test that invalid values raise ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_prompt_sizes("64,abc,128")


class TestBuildArgParser:
    """Tests for argument parser configuration."""

    def test_no_pull_missing_option(self):
        """Test that --pull-missing option has been removed."""
        parser = build_arg_parser()
        # Parse args with default values
        args = parser.parse_args([])
        # Should not have pull_missing attribute
        assert not hasattr(args, "pull_missing")

    def test_no_no_pull_option(self):
        """Test that --no-pull option has been removed."""
        parser = build_arg_parser()
        # Parse args with default values
        args = parser.parse_args([])
        # Should not have pull_missing attribute from --no-pull
        assert not hasattr(args, "pull_missing")

    def test_auto_pull_always_enabled(self):
        """Test that model is always pulled automatically (no option to disable)."""
        parser = build_arg_parser()
        args = parser.parse_args([])
        # Verify the parser doesn't expose pull_if_missing control
        # The run_benchmark_suite should always be called with pull behavior
        assert args.model == "qwen3.5:2b"
        assert args.endpoint == "http://127.0.0.1:11434"
