# Phase 1 — Observability & Documentation (Low Risk)

## Overview

Phase 1 deploys **4 MCP servers in read-only mode** to gain visibility into the Azure Landing Zone and establish documentation workflows. No write operations are enabled — this phase is purely observational.

**MCP Servers**: Azure MCP, AKS MCP, Kubernetes MCP, Atlassian Rovo MCP

**Risk level**: Low — all servers operate in read-only mode

**Estimated setup time**: 1–2 hours per server

---

## Prerequisites

- VS Code with GitHub Copilot extension (Agent mode enabled)
- GitHub Copilot CLI installed
- Node.js 20+ (for npx-based servers)
- Azure CLI installed and authenticated (`az login`)
- `kubectl` configured with AKS cluster access
- Atlassian Cloud account with Rovo enabled

---

## Step 1: Azure MCP Server

### 1.1 Install

Install the VS Code extension (recommended):

```bash
code --install-extension ms-azuretools.vscode-azure-mcp-server
```

Or configure manually in `.vscode/mcp.json`:

```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--mode", "consolidated", "--read-only"]
    }
  }
}
```

### 1.2 Authenticate

```bash
az login
az account set --subscription "<your-subscription-id>"
```

### 1.3 Configure for Read-Only

If using the VS Code extension, set in VS Code settings:

```json
{
  "azureMcp.serverMode": "consolidated",
  "azureMcp.readOnly": true
}
```

### 1.4 Validate

Open VS Code Copilot Chat in **Agent mode** and test:

- _"List all resource groups in my subscription"_
- _"Show me Azure Monitor metrics for my AKS cluster"_
- _"What are the Azure Advisor recommendations for my subscription?"_
- _"List all storage accounts"_

### 1.5 Copilot CLI Setup

```bash
# Add Azure MCP to Copilot CLI
# Configure in ~/.copilot/mcp-config.json
```

```json
{
  "mcpServers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--mode", "consolidated", "--read-only"]
    }
  }
}
```

---

## Step 2: AKS MCP Server

### 2.1 Install

Download the binary from [Azure/aks-mcp releases](https://github.com/Azure/aks-mcp/releases) or build from source:

```bash
go install github.com/Azure/aks-mcp@latest
```

### 2.2 Configure

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "aks": {
      "command": "aks-mcp",
      "args": ["--transport", "stdio", "--access-level", "readonly"]
    }
  }
}
```

> **Important**: Use `--access-level readonly` for Phase 1. This restricts to read operations only (get, describe, logs, list).

### 2.3 Authenticate

AKS MCP uses your existing Azure CLI session:

```bash
az login
az aks get-credentials --resource-group <rg> --name <cluster-name>
```

### 2.4 Validate

Test in VS Code Copilot Chat:

- _"List all AKS clusters in my subscription"_
- _"Show me the network configuration of my AKS cluster"_
- _"What node pools are running and what's their status?"_
- _"Run the node-health diagnostic detector on my cluster"_
- _"Show me control plane logs for the last 30 minutes"_

---

## Step 3: Kubernetes MCP Server

### 3.1 Install

No installation required — runs via npx.

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "kubernetes-mcp-server@latest"]
    }
  }
}
```

### 3.2 Configure for Read-Only

The Kubernetes MCP server can be restricted with a TOML config file. Create `k8s-mcp-config.toml`:

```toml
[server]
read-only = true
```

Then reference it:

```json
{
  "servers": {
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "kubernetes-mcp-server@latest", "--config", "/path/to/k8s-mcp-config.toml"]
    }
  }
}
```

### 3.3 Authenticate

Uses your existing kubeconfig (`~/.kube/config`). Ensure context is set:

```bash
kubectl config current-context
kubectl config use-context <your-aks-context>
```

### 3.4 Validate

Test in VS Code Copilot Chat:

- _"List all pods in the argocd namespace"_
- _"Show me events in the default namespace"_
- _"Get the logs for the ASO controller pod"_
- _"List all Helm releases across namespaces"_
- _"Describe the deployment nginx in namespace production"_

---

## Step 4: Atlassian Rovo MCP Server

### 4.1 Configure

Atlassian MCP uses HTTP transport with OAuth. Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v2/mcp"
    }
  }
}
```

### 4.2 Authenticate

On first connection, your MCP client will open an OAuth authorization page in the browser:

1. Review and approve the authorization request
2. Select the Atlassian site (Jira/Confluence instance) to connect
3. Grant the requested scopes

Admin prerequisites:
- Ensure your Atlassian admin has enabled MCP server connections
- Verify your account has access to the target Jira project and Confluence space

### 4.3 Validate

Test in VS Code Copilot Chat:

- _"Search Confluence for incident postmortems"_
- _"Find Jira issues assigned to me in the SRE project"_
- _"Search for the latest architecture decision records"_
- _"Find Confluence pages about our AKS cluster setup"_

---

## Phase 1 Complete Configuration

Combined `.vscode/mcp.json` for Phase 1:

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
    }
  }
}
```

---

## Validation Checklist

- [ ] Azure MCP responds to resource listing queries
- [ ] AKS MCP returns cluster health and diagnostics
- [ ] Kubernetes MCP lists pods, events, and Helm releases
- [ ] Atlassian MCP returns Jira issues and Confluence search results
- [ ] All servers operate in read-only mode (no mutations possible)
- [ ] Copilot CLI can query Azure MCP and AKS MCP from the terminal

---

## Example Incident Response Workflow (Phase 1)

With these 4 servers, you can already perform an observability-driven incident response:

1. **Detect**: _"Show me degraded pods across all namespaces"_ → Kubernetes MCP
2. **Scope**: _"What's the AKS cluster health status?"_ → AKS MCP
3. **Correlate**: _"Query Log Analytics for errors in the last hour"_ → Azure MCP
4. **Document**: _"Find the Confluence page for the payment-service runbook"_ → Atlassian MCP

---

## Next Phase

Once comfortable with read-only observability, proceed to [Phase 2 — IaC & Quality](phase2-iac-quality.md) to add Terraform, SonarQube, and GitLab MCP servers.
