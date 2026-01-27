"""Tests for production readiness improvements.

This module tests the enhancements made to improve robustness, error handling,
and input validation across the xAI SDK.
"""

import pytest

from xai_sdk.search import web_source
from xai_sdk.tools import web_search, x_search


class TestParameterValidation:
    """Test parameter validation for mutually exclusive arguments."""

    def test_web_search_rejects_both_excluded_and_allowed_domains(self):
        """Test that web_search raises ValueError when both excluded and allowed domains are provided."""
        with pytest.raises(ValueError) as exc_info:
            web_search(
                excluded_domains=["example.com"],
                allowed_domains=["allowed.com"],
            )

        assert "Cannot specify both" in str(exc_info.value)
        assert "excluded_domains" in str(exc_info.value)
        assert "allowed_domains" in str(exc_info.value)

    def test_web_search_accepts_only_excluded_domains(self):
        """Test that web_search works correctly with only excluded_domains."""
        tool = web_search(excluded_domains=["example.com", "spam.com"])
        assert tool is not None
        assert tool.HasField("web_search")

    def test_web_search_accepts_only_allowed_domains(self):
        """Test that web_search works correctly with only allowed_domains."""
        tool = web_search(allowed_domains=["trusted.com"])
        assert tool is not None
        assert tool.HasField("web_search")

    def test_web_search_accepts_neither_domain_parameter(self):
        """Test that web_search works correctly with neither domain parameter."""
        tool = web_search()
        assert tool is not None
        assert tool.HasField("web_search")

    def test_x_search_rejects_both_allowed_and_excluded_handles(self):
        """Test that x_search raises ValueError when both allowed and excluded handles are provided."""
        with pytest.raises(ValueError) as exc_info:
            x_search(
                allowed_x_handles=["xai"],
                excluded_x_handles=["spam_account"],
            )

        assert "Cannot specify both" in str(exc_info.value)
        assert "allowed_x_handles" in str(exc_info.value)
        assert "excluded_x_handles" in str(exc_info.value)

    def test_x_search_accepts_only_allowed_handles(self):
        """Test that x_search works correctly with only allowed_x_handles."""
        tool = x_search(allowed_x_handles=["xai", "elonmusk"])
        assert tool is not None
        assert tool.HasField("x_search")

    def test_x_search_accepts_only_excluded_handles(self):
        """Test that x_search works correctly with only excluded_x_handles."""
        tool = x_search(excluded_x_handles=["spam_account"])
        assert tool is not None
        assert tool.HasField("x_search")

    def test_x_search_accepts_neither_handle_parameter(self):
        """Test that x_search works correctly with neither handle parameter."""
        tool = x_search()
        assert tool is not None
        assert tool.HasField("x_search")

    def test_web_source_rejects_both_excluded_and_allowed_websites(self):
        """Test that web_source raises ValueError when both excluded and allowed websites are provided."""
        with pytest.raises(ValueError) as exc_info:
            web_source(
                excluded_websites=["example.com"],
                allowed_websites=["allowed.com"],
            )

        assert "Cannot specify both" in str(exc_info.value)
        assert "excluded_websites" in str(exc_info.value)
        assert "allowed_websites" in str(exc_info.value)

    def test_web_source_accepts_only_excluded_websites(self):
        """Test that web_source works correctly with only excluded_websites."""
        source = web_source(excluded_websites=["example.com"])
        assert source is not None
        assert source.HasField("web")

    def test_web_source_accepts_only_allowed_websites(self):
        """Test that web_source works correctly with only allowed_websites."""
        source = web_source(allowed_websites=["trusted.com"])
        assert source is not None
        assert source.HasField("web")

    def test_web_source_accepts_neither_website_parameter(self):
        """Test that web_source works correctly with neither website parameter."""
        source = web_source()
        assert source is not None
        assert source.HasField("web")


class TestClientCleanup:
    """Test robust channel cleanup in client close methods."""

    def test_sync_client_cleanup_handles_exceptions(self):
        """Test that sync client close handles exceptions gracefully."""
        from unittest.mock import MagicMock, patch

        from xai_sdk import Client

        # Create a client with mocked channels
        with patch("xai_sdk.sync.client.grpc.secure_channel") as mock_secure_channel:
            mock_channel = MagicMock()
            mock_secure_channel.return_value = mock_channel

            client = Client(api_key="test-key")

            # Mock the close method to raise an exception
            client._api_channel.close = MagicMock(side_effect=Exception("Close failed"))
            client._management_channel = None

            # Should raise the exception but not crash
            with pytest.raises(Exception) as exc_info:
                client.close()

            assert "Close failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_client_cleanup_handles_exceptions(self):
        """Test that async client close handles exceptions gracefully."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from xai_sdk import AsyncClient

        # Create a client with mocked channels
        with patch("xai_sdk.aio.client.grpc.aio.secure_channel") as mock_secure_channel:
            mock_channel = MagicMock()
            mock_secure_channel.return_value = mock_channel

            client = AsyncClient(api_key="test-key")

            # Mock the close method to raise an exception
            client._api_channel.close = AsyncMock(side_effect=Exception("Async close failed"))
            client._management_channel = None

            # Should raise the exception but not crash
            with pytest.raises(Exception) as exc_info:
                await client.close()

            assert "Async close failed" in str(exc_info.value)

    def test_sync_client_cleanup_attempts_both_channels(self):
        """Test that sync client attempts to close both channels even if one fails."""
        from unittest.mock import MagicMock, patch

        from xai_sdk import Client

        with patch("xai_sdk.sync.client.grpc.secure_channel") as mock_secure_channel:
            mock_channel = MagicMock()
            mock_secure_channel.return_value = mock_channel

            client = Client(api_key="test-key")

            # Create mock channels
            management_channel = MagicMock()
            api_channel = MagicMock()

            client._management_channel = management_channel
            client._api_channel = api_channel

            # Make management channel fail
            management_channel.close = MagicMock(side_effect=Exception("Management close failed"))
            api_channel.close = MagicMock()

            # Should raise exception from management channel but still attempt to close api channel
            with pytest.raises(Exception) as exc_info:
                client.close()

            assert "Management close failed" in str(exc_info.value)
            # Verify both close methods were called
            management_channel.close.assert_called_once()
            api_channel.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_client_cleanup_attempts_both_channels(self):
        """Test that async client attempts to close both channels even if one fails."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from xai_sdk import AsyncClient

        with patch("xai_sdk.aio.client.grpc.aio.secure_channel") as mock_secure_channel:
            mock_channel = MagicMock()
            mock_secure_channel.return_value = mock_channel

            client = AsyncClient(api_key="test-key")

            # Create mock channels
            management_channel = MagicMock()
            api_channel = MagicMock()

            client._management_channel = management_channel
            client._api_channel = api_channel

            # Make management channel fail
            management_channel.close = AsyncMock(side_effect=Exception("Async management close failed"))
            api_channel.close = AsyncMock()

            # Should raise exception from management channel but still attempt to close api channel
            with pytest.raises(Exception) as exc_info:
                await client.close()

            assert "Async management close failed" in str(exc_info.value)
            # Verify both close methods were called
            management_channel.close.assert_called_once()
            api_channel.close.assert_called_once()


class TestErrorMessages:
    """Test that error messages are clear and helpful."""

    def test_web_search_error_message_is_descriptive(self):
        """Test that web_search error message provides clear guidance."""
        with pytest.raises(ValueError) as exc_info:
            web_search(
                excluded_domains=["example.com"],
                allowed_domains=["allowed.com"],
            )

        error_message = str(exc_info.value)
        # Check that the error message is helpful
        assert "Cannot specify both" in error_message
        assert "excluded_domains" in error_message
        assert "allowed_domains" in error_message
        assert "only one parameter" in error_message

    def test_x_search_error_message_is_descriptive(self):
        """Test that x_search error message provides clear guidance."""
        with pytest.raises(ValueError) as exc_info:
            x_search(
                allowed_x_handles=["xai"],
                excluded_x_handles=["spam"],
            )

        error_message = str(exc_info.value)
        # Check that the error message is helpful
        assert "Cannot specify both" in error_message
        assert "allowed_x_handles" in error_message
        assert "excluded_x_handles" in error_message
        assert "only one parameter" in error_message

    def test_web_source_error_message_is_descriptive(self):
        """Test that web_source error message provides clear guidance."""
        with pytest.raises(ValueError) as exc_info:
            web_source(
                excluded_websites=["example.com"],
                allowed_websites=["allowed.com"],
            )

        error_message = str(exc_info.value)
        # Check that the error message is helpful
        assert "Cannot specify both" in error_message
        assert "excluded_websites" in error_message
        assert "allowed_websites" in error_message
        assert "only one parameter" in error_message
