"""Tests for the MCP version checker."""

import json
from unittest.mock import patch, MagicMock

import pytest

from sre_mcp_toolkit.registry import SERVERS, MCPServerDef
from sre_mcp_toolkit.versions import (
    fetch_version,
    fetch_all_versions,
    get_github_latest,
    get_npm_latest,
    VersionResult,
)


class TestRegistry:
    """Tests for the MCP server registry."""

    def test_registry_has_8_servers(self):
        assert len(SERVERS) == 8

    def test_registry_has_5_core(self):
        core = [s for s in SERVERS if s.tier == "core"]
        assert len(core) == 5

    def test_registry_has_3_ecosystem(self):
        eco = [s for s in SERVERS if s.tier == "ecosystem"]
        assert len(eco) == 3

    def test_all_servers_have_required_fields(self):
        for s in SERVERS:
            assert s.name, f"Missing name for {s}"
            assert s.tier in ("core", "ecosystem"), f"Invalid tier for {s.name}"
            assert s.source_type, f"Missing source_type for {s.name}"
            assert s.source_id, f"Missing source_id for {s.name}"
            assert s.homepage.startswith("http"), f"Invalid homepage for {s.name}"


class TestFetchVersion:
    """Tests for version fetching."""

    @patch("sre_mcp_toolkit.versions._fetch_json")
    def test_github_latest(self, mock_fetch):
        mock_fetch.return_value = {"tag_name": "v1.2.3"}
        result = get_github_latest("owner/repo")
        assert result == "v1.2.3"

    @patch("sre_mcp_toolkit.versions._fetch_json")
    def test_npm_latest(self, mock_fetch):
        mock_fetch.return_value = {"version": "2.0.0"}
        result = get_npm_latest("my-package")
        assert result == "2.0.0"

    def test_managed_service_returns_managed(self):
        server = MCPServerDef(
            name="Test SaaS",
            tier="core",
            source_type="gitlab",
            source_id="gitlab",
            homepage="https://example.com",
        )
        result = fetch_version(server)
        assert result.latest_version == "managed-service"
        assert result.error is None

    @patch("sre_mcp_toolkit.versions._fetch_json")
    def test_github_error_returns_error_result(self, mock_fetch):
        import urllib.error

        mock_fetch.side_effect = urllib.error.HTTPError(
            url="https://api.github.com",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )
        server = MCPServerDef(
            name="Missing Repo",
            tier="ecosystem",
            source_type="github",
            source_id="no/repo",
            homepage="https://example.com",
        )
        result = fetch_version(server)
        assert result.latest_version == "error"
        assert "404" in result.error

    @patch("sre_mcp_toolkit.versions.fetch_version")
    def test_fetch_all_versions_returns_all(self, mock_fv):
        mock_fv.return_value = VersionResult(
            server_name="test",
            tier="core",
            latest_version="1.0.0",
            source="test",
            homepage="https://example.com",
        )
        results = fetch_all_versions()
        assert len(results) == 8
