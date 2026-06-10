"""Version checker — fetches latest versions from GitHub releases, npm registry."""

import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional

from sre_mcp_toolkit.registry import MCPServerDef

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15


@dataclass
class VersionResult:
    """Result of a version lookup."""

    server_name: str
    tier: str
    latest_version: str
    source: str
    homepage: str
    error: Optional[str] = None


def _github_headers(token: Optional[str] = None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sre-mcp-toolkit/0.1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_json(url: str, headers: Optional[dict] = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def get_github_latest(owner_repo: str, token: Optional[str] = None) -> str:
    """Get latest release tag from a GitHub repository."""
    url = f"https://api.github.com/repos/{owner_repo}/releases/latest"
    data = _fetch_json(url, _github_headers(token))
    return data.get("tag_name", "unknown")


def get_npm_latest(package_name: str) -> str:
    """Get latest version from the npm registry."""
    encoded = package_name.replace("/", "%2F")
    url = f"https://registry.npmjs.org/{encoded}/latest"
    headers = {"Accept": "application/json", "User-Agent": "sre-mcp-toolkit/0.1"}
    data = _fetch_json(url, headers)
    return data.get("version", "unknown")


def fetch_version(
    server: MCPServerDef, github_token: Optional[str] = None
) -> VersionResult:
    """Fetch the latest version for a single MCP server."""
    try:
        if server.source_type == "github":
            version = get_github_latest(server.source_id, github_token)
            source = f"github:{server.source_id}"
        elif server.source_type == "npm":
            version = get_npm_latest(server.source_id)
            source = f"npm:{server.source_id}"
        elif server.source_type in ("gitlab", "atlassian"):
            # Managed SaaS — no versioned release to track
            version = "managed-service"
            source = f"{server.source_type} (SaaS, no public release)"
        else:
            version = "unknown"
            source = server.source_type

        return VersionResult(
            server_name=server.name,
            tier=server.tier,
            latest_version=version,
            source=source,
            homepage=server.homepage,
        )
    except urllib.error.HTTPError as exc:
        logger.warning("HTTP %s for %s: %s", exc.code, server.name, exc.reason)
        return VersionResult(
            server_name=server.name,
            tier=server.tier,
            latest_version="error",
            source=server.source_type,
            homepage=server.homepage,
            error=f"HTTP {exc.code}: {exc.reason}",
        )
    except Exception as exc:
        logger.warning("Failed to fetch version for %s: %s", server.name, exc)
        return VersionResult(
            server_name=server.name,
            tier=server.tier,
            latest_version="error",
            source=server.source_type,
            homepage=server.homepage,
            error=str(exc),
        )


def fetch_all_versions(
    github_token: Optional[str] = None,
) -> list[VersionResult]:
    """Fetch latest versions for all registered MCP servers."""
    from sre_mcp_toolkit.registry import SERVERS

    results = []
    for server in SERVERS:
        result = fetch_version(server, github_token)
        results.append(result)
    return results
