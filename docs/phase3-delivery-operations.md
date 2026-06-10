# Phase 3 — Delivery & Operations (Higher Risk, Controlled)

## Overview

Phase 3 enables **write operations** on existing servers and adds the **ArgoCD MCP** server for GitOps delivery. This phase introduces mutation capabilities and requires careful access control.

**MCP Server added**: ArgoCD MCP

**Servers upgraded**: Terraform MCP (+ TFE_TOKEN), AKS MCP (→ readwrite), Azure MCP (→ write enabled)

**Cumulative total**: 8 MCP servers (all operational)

**Risk level**: Higher — write operations enabled, production-impacting changes possible

**Estimated setup time**: 2–3 hours (including access control review)

---

## Prerequisites

- Phase 1 and Phase 2 completed and validated
- ArgoCD instance with API access and a generated API token
- HCP Terraform / Terraform Enterprise API token (`TFE_TOKEN`)
- Reviewed and approved RBAC permissions for write operations
- Documented rollback procedures for each write-enabled server

---

## Step 1: ArgoCD MCP Server

### 1.1 Generate ArgoCD API Token

```bash
# Option 1: Generate via ArgoCD CLI
argocd account generate-token --account <account-name>

# Option 2: Via ArgoCD UI
# Settings → Accounts → <account> → Generate New Token
```

Store the token securely — do not commit it to version control.

### 1.2 Configure (Read-Only First)

Start with read-only mode to validate connectivity before enabling writes.

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "argocd": {
      "command": "npx",
      "args": ["argocd-mcp@latest", "stdio"],
      "env": {
        "ARGOCD_BASE_URL": "https://argocd.your-domain.com",
        "ARGOCD_API_TOKEN": "<your-argocd-token>",
        "MCP_READ_ONLY": "true"
      }
    }
  }
}
```

### 1.3 Self-Signed Certificates

If your ArgoCD instance uses self-signed certificates:

```json
{
  "servers": {
    "argocd": {
      "command": "npx",
      "args": ["argocd-mcp@latest", "stdio"],
      "env": {
        "ARGOCD_BASE_URL": "https://argocd.your-domain.com",
        "ARGOCD_API_TOKEN": "<your-argocd-token>",
        "MCP_READ_ONLY": "true",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}
```

> **Warning**: Only disable TLS verification in development environments.

### 1.4 Validate (Read-Only)

Test in VS Code Copilot Chat:

- _"List all ArgoCD applications"_
- _"Show me the sync status of the payment-service app"_
- _"Get the resource tree for the api-gateway application"_
- _"List all clusters registered in ArgoCD"_
- _"Show me the workload logs for the payment-service app"_

### 1.5 Enable Write Operations

Once read-only mode is validated, remove the read-only flag:

```json
{
  "servers": {
    "argocd": {
      "command": "npx",
      "args": ["argocd-mcp@latest", "stdio"],
      "env": {
        "ARGOCD_BASE_URL": "https://argocd.your-domain.com",
        "ARGOCD_API_TOKEN": "<your-argocd-token>"
      }
    }
  }
}
```

Now available:
- `sync_application` — Trigger sync operations
- `create_application` — Create new ArgoCD applications
- `update_application` — Update application configuration
- `delete_application` — Delete applications
- `run_resource_action` — Run actions on resources

---

## Step 2: Upgrade Terraform MCP (+ TFE_TOKEN)

### 2.1 Generate HCP Terraform Token

1. Log into [app.terraform.io](https://app.terraform.io) (or your Terraform Enterprise instance)
2. Navigate to **User Settings → Tokens → Create an API token**
3. Choose appropriate scope (organization or team token)

### 2.2 Update Configuration

Replace the Phase 2 Terraform MCP config with the authenticated version:

```json
{
  "servers": {
    "terraform": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TFE_TOKEN",
        "-e", "TFE_ADDRESS",
        "hashicorp/terraform-mcp-server"
      ],
      "env": {
        "TFE_TOKEN": "<your-tfe-token>",
        "TFE_ADDRESS": "https://app.terraform.io"
      }
    }
  }
}
```

> **Note**: `ENABLE_TF_OPERATIONS` is **not set** by default, meaning destructive operations (workspace delete, run apply/discard) are disabled. Enable only when explicitly needed.

### 2.3 Validate New Capabilities

Test in VS Code Copilot Chat:

- _"List all Terraform organizations I have access to"_
- _"Show me workspaces in the infrastructure organization"_
- _"What's the status of the last run in the production-aks workspace?"_
- _"List variables in the staging-network workspace"_
- _"Show me the plan output for the latest run"_

### 2.4 Enable Destructive Operations (Optional, Use with Caution)

Only if needed — add `ENABLE_TF_OPERATIONS`:

```json
{
  "env": {
    "TFE_TOKEN": "<your-tfe-token>",
    "TFE_ADDRESS": "https://app.terraform.io",
    "ENABLE_TF_OPERATIONS": "true"
  }
}
```

This unlocks:
- `create_run` — Queue new Terraform runs
- `action_run` — Apply, discard, or cancel runs
- `delete_workspace_safely` — Delete empty workspaces
- `create_workspace` / `update_workspace` — Workspace lifecycle

---

## Step 3: Upgrade AKS MCP (→ readwrite)

### 3.1 Update Access Level

Change from `readonly` to `readwrite`:

```json
{
  "servers": {
    "aks": {
      "command": "aks-mcp",
      "args": ["--transport", "stdio", "--access-level", "readwrite"]
    }
  }
}
```

### 3.2 New Capabilities (readwrite)

In addition to Phase 1 read operations, now available:

- `create` / `delete` AKS clusters
- `scale` / `start` / `stop` clusters
- `upgrade` Kubernetes version
- `nodepool-add` / `nodepool-delete` / `nodepool-scale` / `nodepool-upgrade`
- `account-set` — Set active subscription

### 3.3 Admin Level (Optional)

For credential management, use `admin` level:

```json
{
  "args": ["--transport", "stdio", "--access-level", "admin"]
}
```

This additionally enables:
- `get-credentials` — Get cluster kubectl credentials

### 3.4 Validate

Test in VS Code Copilot Chat:

- _"Scale the worker nodepool to 5 nodes"_
- _"What Kubernetes versions are available for upgrade?"_
- _"Stop the dev AKS cluster to save costs"_

---

## Step 4: Upgrade Azure MCP (→ write enabled)

### 4.1 Remove Read-Only Flag

Update the Azure MCP configuration to remove `--read-only`:

```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--mode", "consolidated"]
    }
  }
}
```

Or via VS Code extension settings:

```json
{
  "azureMcp.serverMode": "consolidated",
  "azureMcp.readOnly": false
}
```

### 4.2 New Capabilities

Write operations now available:

- Create/update/delete Azure resources (storage, compute, networking)
- Manage Key Vault secrets (with elicitation confirmation)
- Create/update managed disks, VMs, VMSS
- Manage App Service web apps (start, stop, restart, deploy)

> **Safety**: Azure MCP still uses **elicitation** — it prompts for user confirmation before accessing sensitive data like Key Vault secrets.

### 4.3 Validate

Test in VS Code Copilot Chat:

- _"Create a storage account named 'sreteststore' in resource group 'sre-rg'"_
- _"Restart web app 'api-service' in resource group 'prod-rg'"_
- _"Add application setting 'LogLevel' with value 'DEBUG' to web app 'api-service'"_

---

## Phase 3 Complete Configuration

Full `.vscode/mcp.json` with all 8 servers:

```json
{
  "servers": {
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start", "--mode", "consolidated"]
    },
    "aks": {
      "command": "aks-mcp",
      "args": ["--transport", "stdio", "--access-level", "readwrite"]
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
      "args": ["run", "-i", "--rm", "-e", "TFE_TOKEN", "-e", "TFE_ADDRESS", "hashicorp/terraform-mcp-server"],
      "env": {
        "TFE_TOKEN": "<your-tfe-token>",
        "TFE_ADDRESS": "https://app.terraform.io"
      }
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
    },
    "argocd": {
      "command": "npx",
      "args": ["argocd-mcp@latest", "stdio"],
      "env": {
        "ARGOCD_BASE_URL": "https://argocd.your-domain.com",
        "ARGOCD_API_TOKEN": "<your-argocd-token>"
      }
    }
  }
}
```

---

## Validation Checklist

- [ ] ArgoCD MCP lists applications and shows sync status
- [ ] ArgoCD MCP can sync an application (test on non-production first)
- [ ] Terraform MCP lists organizations, workspaces, and runs with TFE_TOKEN
- [ ] AKS MCP can scale a nodepool (test on dev cluster first)
- [ ] Azure MCP can create/update resources (test on non-production resource group)
- [ ] Elicitation prompts appear for sensitive Azure operations
- [ ] All 8 MCP servers operate correctly in the same configuration
- [ ] Phase 1 and Phase 2 capabilities remain functional

---

## Safety Recommendations

### Before enabling writes
- [ ] Document rollback procedures for each server
- [ ] Test all write operations on non-production environments first
- [ ] Review Azure RBAC and Kubernetes RBAC permissions
- [ ] Verify ArgoCD account has appropriate project-level restrictions

### Ongoing
- [ ] Monitor Azure Activity Log for MCP-initiated changes
- [ ] Review Atlassian MCP audit logs regularly
- [ ] Rotate API tokens (ArgoCD, SonarQube, Terraform) on schedule
- [ ] Keep MCP server versions up to date

---

## Example Full Delivery Workflow (Phase 3)

With all 8 servers and write operations enabled:

1. **Plan**: _"Show me the Terraform module for AKS with private endpoint"_ → Terraform MCP
2. **Review**: _"Create a merge request for the AKS changes in the infra repo"_ → GitLab MCP
3. **Quality**: _"Check the SonarQube quality gate for the infra project"_ → SonarQube MCP
4. **Provision**: _"List my resource groups and create 'prod-aks-rg' in westeurope"_ → Azure MCP
5. **Deploy**: _"Queue a Terraform run on the production-aks workspace"_ → Terraform MCP
6. **Deliver**: _"Sync the payment-service ArgoCD application"_ → ArgoCD MCP
7. **Verify**: _"Show me the resource tree and health of the payment-service app"_ → ArgoCD MCP
8. **Monitor**: _"What pods are running in the payment namespace?"_ → Kubernetes MCP
9. **Diagnose**: _"Run the node-health detector on the production cluster"_ → AKS MCP
10. **Track**: _"Update the Jira deployment epic and create a Confluence release note"_ → Atlassian MCP
