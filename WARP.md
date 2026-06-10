# Enhanced SRE Ecosystem — Project Rules

## Project Overview

This project defines an MCP-augmented Azure Landing Zone architecture with 8 MCP servers (5 core + 3 ecosystem), phased implementation guides, an MkDocs documentation site, and a Python CLI toolkit (`sre-mcp-toolkit`).

## Repository

- **GitHub**: https://github.com/brunseba/enhanced-sre
- **GitHub Pages**: https://brunseba.github.io/enhanced-sre/

## Project Structure

- `docs/` — MkDocs content (architecture, phase guides, index)
- `inputs/` — Design inputs and plans (mcp-server.md, librechat-plan.md)
- `src/sre_mcp_toolkit/` — Python CLI toolkit source code
- `tests/` — Unit tests (pytest)
- `mkdocs.yml` — MkDocs configuration (Material theme, mermaid, git revision)
- `pyproject.toml` — Python project config (uv, hatchling, click)

## Python

- Version >= 3.10
- Package engine: uv
- Root folder for code: `src`
- CLI managed by click
- Deploy with pipx
- No `.py` files in the root folder
- No function longer than 100 lines
- Always create unit tests

## MkDocs

- Theme: Material
- Track git changes (git-revision-date-localized)
- Support mermaid diagrams (mermaid2 plugin)
- PDF export available (requires native libs, commented out by default)
- Dark mode capability

## Documentation

- `.md` files must be stored in `docs/` folder (except README.md, CHANGELOG.md, LICENSE)
- Architecture docs go in `docs/`
- Design inputs and plans go in `inputs/`

## Git

- Use conventional commits (feat, fix, docs, chore, refactor, etc.)
- Use pre-commit hooks (`.pre-commit-config.yaml`)
- Generate changelog when tagging
- Update `mkdocs.yml` and `docs/index.md` when tagging
- `.gitignore` must map Python, mkdocs, workspace root folder
- Push to GitHub with `git subtree split --prefix=Professionel/enhanced-sre` (repo is a subdirectory of veille-technologique)

## GitHub

- Issue labels map conventional commit standards (feat, fix, docs, style, refactor, perf, test, build, ci, chore)
- New issues assigned to @me by default
- GitHub Pages enabled (workflow-based deployment)
- GitHub Action workflow: `.github/workflows/mkdocs-publish.yml`

## sre-mcp-toolkit CLI

- Entry point: `sre-mcp-toolkit`
- Commands: `versions` (fetch latest MCP server versions), `list-servers` (list registered servers)
- Registry: `src/sre_mcp_toolkit/registry.py` — all 8 MCP servers defined here
- Sources: GitHub Releases API, npm registry; GitLab and Atlassian are managed SaaS
- Set `GITHUB_TOKEN` env var for higher API rate limits

## MCP Servers (8 total)

### Core (from curated list)
1. Azure MCP — Microsoft (npm: @azure/mcp)
2. Terraform MCP — HashiCorp (github: hashicorp/terraform-mcp-server)
3. GitLab MCP — GitLab (HTTP/OAuth, managed SaaS)
4. SonarQube MCP — SonarSource (github: SonarSource/sonarqube-mcp-server)
5. Atlassian Rovo MCP — Atlassian (HTTP/OAuth, managed SaaS)

### Ecosystem (existing servers for ecosystem components)
6. AKS MCP — Azure/aks-mcp (github)
7. ArgoCD MCP — argoproj-labs/mcp-for-argocd (npm: argocd-mcp)
8. Kubernetes MCP — containers/kubernetes-mcp-server (npm)

## Ecosystem Context

- Kubernetes AKS
- ArgoCD GitOps
- Hosted GitLab-CI
- Azure PaaS (PostgreSQL, MySQL, WebApp, Event Hub, APIM, App Gateway, WAF)
- Azure Service Operator (ASO v2)
- Self-hosted SonarQube Community Edition
- MCP clients: VS Code + GitHub Copilot, GitHub Copilot CLI

## Exclusions

- Do not include Warp shell in the architecture design
