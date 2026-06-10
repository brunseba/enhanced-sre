# Phase 2 — IaC & Quality (Medium Risk)

## Overview

Phase 2 adds **3 MCP servers** focused on Infrastructure as Code, code quality, and CI/CD visibility. These servers are primarily read-only but connect to external services (hosted GitLab, self-hosted SonarQube, HCP Terraform).

**MCP Servers added**: Terraform MCP, SonarQube MCP, GitLab MCP

**Cumulative total**: 7 MCP servers (4 from Phase 1 + 3 new)

**Risk level**: Medium — read-only access to external services, token-based authentication

**Estimated setup time**: 1–2 hours per server

---

## Prerequisites

- Phase 1 completed and validated
- Docker installed and running (for SonarQube MCP)
- Access to hosted GitLab instance with GitLab Duo enabled (Premium or Ultimate tier)
- Access to self-hosted SonarQube Community Edition instance
- SonarQube user token generated
- (Optional) HCP Terraform account — not required for registry-only usage

---

## Step 1: Terraform MCP Server

### 1.1 Install

Terraform MCP runs as a Docker container. No local installation required.

### 1.2 Configure (Registry Only — No Token)

For Phase 2, start with **registry tools only** (no HCP Terraform token). This provides documentation lookup, module search, and provider discovery without any write capabilities.

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "terraform": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
    }
  }
}
```

> **Note**: Without `TFE_TOKEN`, only public registry tools are available. HCP Terraform workspace management is added in Phase 3.

### 1.3 Validate

Test in VS Code Copilot Chat:

- _"Show me the Terraform AzureRM docs for azurerm_kubernetes_cluster"_
- _"Search for Terraform modules for Azure AKS"_
- _"What's the latest version of the azurerm provider?"_
- _"Find Azure Verified Modules for storage accounts"_
- _"Show me Sentinel policies for AWS S3 security"_

### 1.4 Copilot CLI Setup

```json
{
  "mcpServers": {
    "terraform": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
    }
  }
}
```

---

## Step 2: SonarQube MCP Server

### 2.1 Prerequisites

Generate a SonarQube user token from your self-hosted instance:

1. Log into your SonarQube Community Edition instance
2. Navigate to **My Account → Security → Generate Tokens**
3. Create a token with **User Token** type
4. Copy and store the token securely

### 2.2 Configure

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "sonarqube": {
      "command": "docker",
      "args": [
        "run", "--init", "-i", "--rm",
        "-e", "SONARQUBE_TOKEN",
        "-e", "SONARQUBE_URL",
        "mcp/sonarqube"
      ],
      "env": {
        "SONARQUBE_TOKEN": "<your-sonarqube-token>",
        "SONARQUBE_URL": "https://sonarqube.your-domain.com"
      }
    }
  }
}
```

> **Security**: Store the token in environment variables rather than hardcoding. Use a `.env` file or secret manager integration.

### 2.3 Network Access

Ensure the Docker container can reach your self-hosted SonarQube instance:

- If SonarQube is on your corporate network, the container needs network access
- For VPN-only access, ensure Docker is routed through VPN
- Test connectivity: `curl --connect-timeout 5 --max-time 10 https://sonarqube.your-domain.com/api/system/status`

### 2.4 Validate

Test in VS Code Copilot Chat:

- _"List all projects in SonarQube"_
- _"Show me the quality gate status for the infrastructure project"_
- _"What are the open security hotspots in the api-service project?"_
- _"Analyze this code snippet for quality issues"_ (paste a code block)
- _"Show me the technical debt for the payment-service project"_

### 2.5 Community Edition Limitations

Be aware of Community Edition scope:

- **Available**: Quality profiles, issues, hotspots, quality gates, project analysis
- **Not available**: Branch analysis (only main branch), portfolio management, advanced security rules (OWASP/SANS), project transfer

---

## Step 3: GitLab MCP Server

### 3.1 Prerequisites

GitLab MCP requires:

- Hosted GitLab instance with **Premium or Ultimate** tier
- **GitLab Duo** enabled for the top-level group
- **Beta and experimental features** enabled in group settings

### 3.2 Configure

GitLab MCP uses HTTP transport with OAuth. Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "gitlab": {
      "type": "http",
      "url": "https://gitlab.your-domain.com/api/v4/mcp"
    }
  }
}
```

For GitLab.com (SaaS):

```json
{
  "servers": {
    "gitlab": {
      "type": "http",
      "url": "https://gitlab.com/api/v4/mcp"
    }
  }
}
```

### 3.3 Authenticate

On first connection, GitLab MCP uses OAuth 2.0 Dynamic Client Registration:

1. The MCP client registers itself as an OAuth application with your GitLab instance
2. A browser window opens for OAuth authorization
3. Review and approve the request
4. The access token is stored for subsequent sessions

### 3.4 Validate

Test in VS Code Copilot Chat:

- _"List my GitLab projects"_
- _"Show me open merge requests in the infrastructure project"_
- _"Find issues labeled 'bug' in the api-service repository"_
- _"What pipelines ran on the main branch today?"_
- _"Show me the details of merge request #42 in the payment-service project"_

---

## Phase 2 Complete Configuration

Combined `.vscode/mcp.json` (Phase 1 + Phase 2):

```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--mode", "consolidated", "--read-only"]
    },
    "aks": {
      "command": "aks-mcp",
      "args": ["--transport", "stdio", "--access-level", "readonly"]
    },
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "kubernetes-mcp-server@latest"]
    },
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v2/mcp"
    },
    "terraform": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
    },
    "sonarqube": {
      "command": "docker",
      "args": ["run", "--init", "-i", "--rm", "-e", "SONARQUBE_TOKEN", "-e", "SONARQUBE_URL", "mcp/sonarqube"],
      "env": {
        "SONARQUBE_TOKEN": "<your-sonarqube-token>",
        "SONARQUBE_URL": "https://sonarqube.your-domain.com"
      }
    },
    "gitlab": {
      "type": "http",
      "url": "https://gitlab.your-domain.com/api/v4/mcp"
    }
  }
}
```

---

## Validation Checklist

- [ ] Terraform MCP returns provider documentation and module search results
- [ ] SonarQube MCP connects to the self-hosted instance and lists projects
- [ ] SonarQube MCP returns quality gate status and issues
- [ ] GitLab MCP authenticates via OAuth and lists projects
- [ ] GitLab MCP returns merge requests and pipeline status
- [ ] Docker containers can reach SonarQube and Terraform Registry endpoints
- [ ] Phase 1 servers still operate correctly alongside new servers

---

## Example IaC Workflow (Phase 2)

With 7 servers, you can now perform a complete IaC review workflow:

1. **Research**: _"Show me the Terraform AzureRM docs for azurerm_postgresql_flexible_server"_ → Terraform MCP
2. **Discover**: _"Find Azure Verified Modules for PostgreSQL"_ → Terraform MCP
3. **Review**: _"Show me open merge requests in the terraform-infra project"_ → GitLab MCP
4. **Quality**: _"Check the SonarQube quality gate for the terraform-infra project"_ → SonarQube MCP
5. **Context**: _"What resource groups exist in subscription X?"_ → Azure MCP
6. **Document**: _"Create a Jira issue for the PostgreSQL migration task"_ → Atlassian MCP

---

## Next Phase

Once IaC and quality workflows are validated, proceed to [Phase 3 — Delivery & Operations](phase3-delivery-operations.md) to enable write operations and GitOps delivery.
