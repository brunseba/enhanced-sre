# Enhanced SRE Ecosystem

An MCP-augmented Azure Landing Zone architecture leveraging 8 Model Context Protocol servers for AI-assisted SRE operations.

## Quick Start

```bash
# Install dependencies
pip install mkdocs-material mkdocs-mermaid2-plugin mkdocs-git-revision-date-localized-plugin mkdocs-with-pdf

# Serve locally
mkdocs serve

# Build
mkdocs build
```

## Documentation

- **Architecture** — Full ecosystem design with 5 core + 3 ecosystem MCP servers
- **Phase 1** — Observability & Documentation (read-only, low risk)
- **Phase 2** — IaC & Quality (Terraform, SonarQube, GitLab)
- **Phase 3** — Delivery & Operations (ArgoCD, write operations)

## MCP Servers

| Core | Ecosystem |
|---|---|
| Azure MCP | AKS MCP |
| Terraform MCP | ArgoCD MCP |
| GitLab MCP | Kubernetes MCP |
| SonarQube MCP | |
| Atlassian MCP | |

## License

Private — Internal use only.
