"""MCP Server registry — defines all 8 servers and their version sources."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPServerDef:
    """Definition of an MCP server with its version lookup source."""

    name: str
    tier: str  # "core" or "ecosystem"
    source_type: str  # "github", "npm", "docker"
    source_id: str  # owner/repo, package name, or image name
    homepage: str


SERVERS: list[MCPServerDef] = [
    # --- Core (curated list) ---
    MCPServerDef(
        name="Azure MCP",
        tier="core",
        source_type="npm",
        source_id="@azure/mcp",
        homepage="https://github.com/microsoft/mcp",
    ),
    MCPServerDef(
        name="Terraform MCP",
        tier="core",
        source_type="github",
        source_id="hashicorp/terraform-mcp-server",
        homepage="https://github.com/hashicorp/terraform-mcp-server",
    ),
    MCPServerDef(
        name="GitLab MCP",
        tier="core",
        source_type="gitlab",
        source_id="gitlab",
        homepage="https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/",
    ),
    MCPServerDef(
        name="SonarQube MCP",
        tier="core",
        source_type="github",
        source_id="SonarSource/sonarqube-mcp-server",
        homepage="https://github.com/SonarSource/sonarqube-mcp-server",
    ),
    MCPServerDef(
        name="Atlassian Rovo MCP",
        tier="core",
        source_type="atlassian",
        source_id="atlassian",
        homepage="https://www.atlassian.com/blog/rovo/atlassian-rovo-mcp-ga",
    ),
    # --- Ecosystem (existing servers for ecosystem components) ---
    MCPServerDef(
        name="AKS MCP",
        tier="ecosystem",
        source_type="github",
        source_id="Azure/aks-mcp",
        homepage="https://github.com/Azure/aks-mcp",
    ),
    MCPServerDef(
        name="ArgoCD MCP",
        tier="ecosystem",
        source_type="npm",
        source_id="argocd-mcp",
        homepage="https://github.com/argoproj-labs/mcp-for-argocd",
    ),
    MCPServerDef(
        name="Kubernetes MCP",
        tier="ecosystem",
        source_type="npm",
        source_id="kubernetes-mcp-server",
        homepage="https://github.com/containers/kubernetes-mcp-server",
    ),
]
