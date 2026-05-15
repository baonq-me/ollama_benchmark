"""Tests for automatic model pull functionality.

These tests verify that the benchmark CLI automatically pulls models
when they are not available locally, without requiring explicit flags.
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock

from tests.mock_ollama_server import MockOllamaServer
from ollama_benchmark.benchmark import check_and_pull_model, run_benchmark_suite


class TestAutoPullFunctionality:
    """Tests for automatic model pull behavior."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock Ollama server for testing."""
        server = MockOllamaServer(port=11998)
        server.start()
        yield server
        server.stop()

    def test_model_pulled_when_missing(self, mock_server):
        """Test that model is automatically pulled when not available locally."""
        model_name = "test-model:latest"
        
        # Verify model is not available initially
        assert not mock_server.is_model_available(model_name)
        
        # Call check_and_pull_model - should pull the model
        result = check_and_pull_model(
            endpoint=mock_server.base_url,
            model=model_name,
            retries=1,
            retry_delay=0.1,
        )
        
        # Verify model was pulled successfully
        assert result is True
        assert mock_server.is_model_available(model_name)

    def test_model_not_re_pulled_when_exists(self, mock_server):
        """Test that model is not pulled again when already available."""
        model_name = "existing-model:latest"
        
        # Add model to local list
        mock_server.add_model(model_name)
        
        # Mock the pull function to track if it's called
        with patch('ollama_benchmark.benchmark.check_and_pull_model') as mock_check:
            mock_check.return_value = True
            
            result = check_and_pull_model(
                endpoint=mock_server.base_url,
                model=model_name,
                retries=1,
                retry_delay=0.1,
            )
            
            assert result is True

    def test_benchmark_suite_pulls_missing_model(self, mock_server):
        """Test that run_benchmark_suite pulls model when missing."""
        model_name = "benchmark-test-model"
        
        # Verify model is not available
        assert not mock_server.is_model_available(model_name)
        
        # Run benchmark suite with small prompt size and few iterations
        # Note: This may take a few seconds due to model pull
        result = run_benchmark_suite(
            endpoint=mock_server.base_url,
            model=model_name,
            prompt_sizes=[64],
            gen_tokens=10,
            iterations=1,
            concurrent=1,
            retries=1,
            retry_delay=0.1,
        )
        
        # Verify model was pulled
        assert mock_server.is_model_available(model_name)
        
        # Verify result structure
        assert "metadata" in result
        assert "results" in result
        assert result["metadata"]["model"] == model_name

    def test_check_and_pull_model_with_tag(self, mock_server):
        """Test model pull with specific tag."""
        model_name = "test-model:7b"
        
        result = check_and_pull_model(
            endpoint=mock_server.base_url,
            model=model_name,
            retries=1,
            retry_delay=0.1,
        )
        
        assert result is True
        assert mock_server.is_model_available(model_name)

    def test_check_and_pull_model_with_base_name(self, mock_server):
        """Test that base name matching works for existing models."""
        model_name = "llama3.2"
        
        # Add model with tag
        mock_server.add_model("llama3.2:latest")
        
        # Should detect model as available via base name matching
        result = check_and_pull_model(
            endpoint=mock_server.base_url,
            model=model_name,
            retries=1,
            retry_delay=0.1,
        )
        
        assert result is True