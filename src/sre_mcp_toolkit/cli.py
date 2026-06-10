"""CLI for the MCP Toolkit."""

import json
import logging
import os
import sys

import click

from sre_mcp_toolkit import __version__
from sre_mcp_toolkit.versions import fetch_all_versions


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


@click.group()
@click.version_option(version=__version__, prog_name="sre-mcp-toolkit")
def cli() -> None:
    """SRE MCP Toolkit — Integration toolkit for the Enhanced SRE Ecosystem."""


@cli.command()
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON.")
@click.option("--tier", type=click.Choice(["all", "core", "ecosystem"]),
              default="all", help="Filter by tier.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def versions(json_output: bool, tier: str, verbose: bool) -> None:
    """Fetch latest versions of all MCP servers in the SRE ecosystem."""
    _setup_logging(verbose)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        click.echo(
            "ℹ  No GITHUB_TOKEN set — GitHub API rate limit is 60 req/h. "
            "Set GITHUB_TOKEN or GH_TOKEN for higher limits.",
            err=True,
        )

    results = fetch_all_versions(github_token=token)

    if tier != "all":
        results = [r for r in results if r.tier == tier]

    if json_output:
        data = [
            {
                "name": r.server_name,
                "tier": r.tier,
                "version": r.latest_version,
                "source": r.source,
                "homepage": r.homepage,
                "error": r.error,
            }
            for r in results
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        _print_table(results)


def _print_table(results: list) -> None:
    """Print results as a formatted table."""
    click.echo()
    click.echo(f"{'Server':<22} {'Tier':<11} {'Version':<20} {'Source'}")
    click.echo("─" * 80)
    for r in results:
        version_str = r.latest_version
        if r.error:
            version_str = click.style(f"✗ {r.error}", fg="red")
        elif r.latest_version == "managed-service":
            version_str = click.style("managed-service", fg="yellow")
        else:
            version_str = click.style(r.latest_version, fg="green")

        click.echo(f"{r.server_name:<22} {r.tier:<11} {version_str:<30} {r.source}")
    click.echo()


@cli.command()
def list_servers() -> None:
    """List all registered MCP servers."""
    from sre_mcp_toolkit.registry import SERVERS

    click.echo()
    click.echo(f"{'Server':<22} {'Tier':<11} {'Type':<10} {'Source ID'}")
    click.echo("─" * 70)
    for s in SERVERS:
        click.echo(f"{s.name:<22} {s.tier:<11} {s.source_type:<10} {s.source_id}")
    click.echo()
    click.echo(f"Total: {len(SERVERS)} servers")


def main() -> None:
    """Entry point."""
    cli()
