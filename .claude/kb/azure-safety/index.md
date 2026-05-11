# Azure Safety Knowledge Base

> **Purpose**: Reference for safe Azure CLI operations — what the hook blocks, why, and safe alternatives
> **MCP Validated**: 2026-05-08

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/azure-destructive-operations.md](concepts/azure-destructive-operations.md) | What each blocked command does and why it's dangerous |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/safe-azure-operations.md](patterns/safe-azure-operations.md) | Safe patterns for resource groups, VMs, storage, functions, AKS |
| [patterns/azure-least-privilege.md](patterns/azure-least-privilege.md) | RBAC least-privilege patterns (Reader, Contributor scopes) |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Blocked vs safe command cheat sheet

---

## Hook Reference

The `pre-bash-cloud-safety.js` hook intercepts Bash tool calls before execution and blocks the following:

| Pattern Blocked | Scope |
|-----------------|-------|
| `az group delete` | Any resource group |
| `az vm delete` / `az vmss delete` | Any VM or scale set |
| `az storage account delete` | Any storage account |
| `az functionapp delete` | Any function app |
| `az aks delete` | Any Kubernetes cluster |
| `az keyvault delete` | Any Key Vault |
| `az sql server delete` / `az sql db delete` | Any SQL server or database |
| `--resource-group *-prod*` | Any command targeting prod RGs |
| `--resource-group *-production*` | Any command targeting production RGs |

**Hook behavior:** The hook stops execution and prints an explanation. The user must explicitly confirm before the command runs.

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Destructive operation** | Any CLI command that permanently deletes or irrecoverably modifies a resource |
| **Production guard** | Resource group name pattern matching (`*-prod*`, `*-production*`) stops all commands |
| **Least privilege** | Each service principal gets only the roles required for its specific task |
| **Soft delete** | Azure feature on Key Vault and Storage that enables recovery within retention window |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Start here** | quick-reference.md |
| **Understand risks** | concepts/azure-destructive-operations.md |
| **Safe operations** | patterns/safe-azure-operations.md |
| **Access control** | patterns/azure-least-privilege.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| infra-deployer | patterns/safe-azure-operations.md | Deploying or modifying Azure resources safely |
| code-reviewer | concepts/azure-destructive-operations.md | Reviewing scripts for dangerous commands |
