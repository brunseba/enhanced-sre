# LibreChat.ai Integration into Enhanced SRE Ecosystem

## Problem Statement

The current SRE ecosystem relies on VS Code + GitHub Copilot and Copilot CLI as MCP clients. These are developer-centric tools that require local installation and individual configuration. There is no **shared, web-based AI interface** accessible to the broader SRE/ops team (on-call engineers, managers, stakeholders) without IDE setup.

## What is LibreChat?

LibreChat is a **self-hosted, open-source AI chat platform** (MIT license, 37K+ GitHub stars) that provides:

- ChatGPT-like web UI with multi-model support (OpenAI, Anthropic, Azure, Bedrock, local models)
- **Native MCP server integration** (stdio, SSE, streamable-http, WebSocket transports)
- **Agent builder** — no-code custom AI assistants with MCP tools, skills, code execution
- Multi-user auth (OAuth2, LDAP, SAML, OIDC) with role-based access
- Per-user MCP credentials (each user can supply their own API tokens)
- Conversation history, search, export
- Docker Compose deployment

## Value for the SRE Ecosystem

### Gap Analysis

| Capability | Current (VS Code + Copilot CLI) | With LibreChat |
|---|---|---|
| Web-based access | ❌ None | ✅ Browser-based, no install |
| Shared team workspace | ❌ Individual setups | ✅ Centralized, multi-user |
| Non-developer access | ❌ Requires IDE | ✅ Any browser user |
| Pre-built SRE agents | ❌ Ad-hoc prompts | ✅ Reusable agents with MCP tools |
| Auth integration | GitHub-only | ✅ OIDC, LDAP, SAML, OAuth2 |
| Audit & conversation history | ❌ Local only | ✅ Server-side, searchable |
| Model flexibility | GitHub Copilot models only | ✅ Any provider: OpenAI, Azure OpenAI, Anthropic, local |
| On-call incident portal | ❌ No shared UI | ✅ Shared agents for incident response |

### Key Use Cases

1. **SRE Incident Response Portal** — Pre-built agent with Azure MCP + AKS MCP + Atlassian MCP for on-call engineers to diagnose and document incidents from any browser
2. **IaC Self-Service** — Agent with Terraform MCP for platform consumers to look up modules and check workspace status
3. **Quality Dashboard Agent** — Agent with SonarQube MCP for tech leads to check quality gates without SonarQube access
4. **GitOps Visibility** — Agent with ArgoCD MCP + GitLab MCP for delivery managers to check deployment status
5. **Architecture Knowledge Base** — Agent with Atlassian MCP for searching and creating architecture documentation

## Proposed Architecture

LibreChat deploys as a Docker Compose stack (for evaluation purpose) on in AKS (for production) and connects to all 8 MCP servers via `librechat.yaml`. It complements VS Code/Copilot CLI — not replaces them.

```
┌─────────────────────────────────────────────────┐
│              AI Client Layer                     │
├──────────┬──────────────┬───────────────────────┤
│ VS Code  │ Copilot CLI  │ LibreChat (Web UI)    │
│ (dev)    │ (terminal)   │ (team-wide, browser)  │
├──────────┴──────────────┴───────────────────────┤
│           8 MCP Servers (shared)                 │
├─────────────────────────────────────────────────┤
│           Azure Landing Zone                     │
└─────────────────────────────────────────────────┘
```

## Implementation Plan

### Step 1 — Deploy LibreChat on AKS

- Deploy via Docker Compose or Helm on AKS
- Configure OIDC authentication (Azure Entra ID) for SSO
- Set up MongoDB for conversation storage
- Configure S3-compatible storage for file uploads (Azure Blob)
- Expose via Ingress with TLS

### Step 2 — Connect the 8 MCP Servers

Configure all existing MCP servers in `librechat.yaml`:

- **Azure MCP** (npx, consolidated mode)
- **Terraform MCP** (Docker, registry-only initially)
- **GitLab MCP** (HTTP/OAuth)
- **SonarQube MCP** (Docker, self-hosted URL)
- **Atlassian MCP** (HTTP/OAuth)
- **AKS MCP** (stdio via binary)
- **ArgoCD MCP** (npx, stdio)
- **Kubernetes MCP** (npx, stdio)

Use `customUserVars` for per-user tokens (ArgoCD, SonarQube) or admin-provided keys for shared access.

### Step 3 — Build SRE Agents

Create purpose-built agents in the Agent Builder:

- **Incident Responder** — Azure MCP + AKS MCP + K8s MCP + Atlassian MCP, instructions for triage workflow
- **IaC Assistant** — Terraform MCP + Azure MCP + GitLab MCP, instructions for module lookup and workspace inspection
- **Quality Gate Checker** — SonarQube MCP, instructions to report quality status
- **Deployment Tracker** — ArgoCD MCP + GitLab MCP, instructions for sync status and pipeline visibility
- **Architecture Documenter** — Atlassian MCP + Azure MCP, instructions for generating Confluence pages

### Step 4 — RBAC & Security

- Configure `interface.mcpServers` permissions (use: true, create: false for non-admins)
- Restrict write-capable MCP servers to admin-role agents only
- Use per-user credentials for OAuth-based MCP servers (GitLab, Atlassian)
- Admin-provided tokens for shared read-only servers (Azure MCP, SonarQube)

### Step 5 — Validate & Document

- Test each agent with representative prompts
- Create Confluence documentation for team onboarding
- Add LibreChat as a new MCP client in the architecture document

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| MCP server compatibility | LibreChat supports all 4 transports (stdio, SSE, streamable-http, WebSocket); all 8 servers are compatible |
| Auth complexity | OIDC via Azure Entra ID provides SSO; per-user vars handle tool-specific tokens |
| Operational overhead | Docker Compose is lightweight; can run as a single AKS deployment |
| Model cost | LibreChat supports Azure OpenAI (existing enterprise agreement) and local models via Ollama |
| Security | Self-hosted, no data leaves your infra; SSRF protection built-in; conversation data in your MongoDB |
