# Azure Least Privilege Pattern

> **Purpose**: RBAC patterns for assigning the minimum required permissions to service principals and managed identities
> **MCP Validated**: 2026-05-08

## When to Use

- Creating a new service principal for automation or a function app
- Reviewing role assignments before deploying to production
- Scoping permissions to a specific resource rather than the whole subscription

---

## Core Principle

Assign roles at the narrowest scope that works:

```
Subscription > Resource Group > Resource > Child Resource
     (widest)                                  (narrowest)
```

Always prefer resource-level or resource-group-level scope over subscription-level scope.

---

## Built-In Roles Reference

| Role | Scope of Power | Use For |
|------|---------------|---------|
| `Reader` | Read-only on all resources in scope | Monitoring service principals, audit accounts |
| `Contributor` | Create/modify resources, cannot assign roles | CI/CD pipelines, dev automation |
| `Owner` | Full control including role assignment | Avoid — use only for break-glass accounts |
| `Storage Blob Data Reader` | Read blobs only | Services that only consume data |
| `Storage Blob Data Contributor` | Read/write/delete blobs | Services that write data |
| `Storage Queue Data Contributor` | Read/write/delete queue messages | Queue-based workers |
| `Key Vault Secrets User` | Read secret values | Apps reading secrets at runtime |
| `Key Vault Secrets Officer` | Create/delete secrets | CI/CD pipelines managing secrets |
| `AcrPull` | Pull images from ACR | Function apps, AKS node pools |
| `AcrPush` | Push images to ACR | CI/CD build pipelines |
| `Website Contributor` | Deploy and configure Function Apps | Deployment pipelines |

---

## Pattern: Managed Identity (preferred over service principals)

Use system-assigned or user-assigned managed identities for Azure resources. No credentials to rotate.

```bash
# Enable system-assigned managed identity on a function app
az functionapp identity assign \
  --resource-group my-rg-dev \
  --name my-func-dev

# Retrieve the principal ID for role assignment
PRINCIPAL_ID=$(az functionapp identity show \
  --resource-group my-rg-dev \
  --name my-func-dev \
  --query "principalId" \
  --output tsv)

# Grant read access to a specific storage account only
STORAGE_ID=$(az storage account show \
  --resource-group my-rg-dev \
  --name mystoragedev \
  --query "id" \
  --output tsv)

az role assignment create \
  --assignee "$PRINCIPAL_ID" \
  --role "Storage Blob Data Reader" \
  --scope "$STORAGE_ID"
```

---

## Pattern: Service Principal with Resource-Level Scope

Use when managed identity is not available (external CI/CD, cross-tenant).

```bash
# Create service principal without any default role
az ad sp create-for-rbac \
  --name sp-my-pipeline-dev \
  --skip-assignment

SP_APP_ID="<app-id-from-output>"

# Grant Contributor only on the dev resource group (not subscription)
RG_ID=$(az group show \
  --name my-rg-dev \
  --query "id" \
  --output tsv)

az role assignment create \
  --assignee "$SP_APP_ID" \
  --role "Contributor" \
  --scope "$RG_ID"
```

---

## Pattern: AKS Node Pool — ACR Pull Only

AKS node pools need to pull images. Grant `AcrPull` at the registry level, nothing more.

```bash
ACR_ID=$(az acr show \
  --name myregistry \
  --resource-group my-rg-dev \
  --query "id" \
  --output tsv)

AKS_KUBELET_ID=$(az aks show \
  --resource-group my-rg-dev \
  --name my-aks-dev \
  --query "identityProfile.kubeletidentity.objectId" \
  --output tsv)

az role assignment create \
  --assignee "$AKS_KUBELET_ID" \
  --role "AcrPull" \
  --scope "$ACR_ID"
```

---

## Pattern: Function App — Key Vault Secrets Only

A function app should never have `Contributor` on the Key Vault. Grant `Key Vault Secrets User` on the specific vault.

```bash
KV_ID=$(az keyvault show \
  --name my-keyvault-dev \
  --resource-group my-rg-dev \
  --query "id" \
  --output tsv)

az role assignment create \
  --assignee "$PRINCIPAL_ID" \
  --role "Key Vault Secrets User" \
  --scope "$KV_ID"
```

---

## Auditing Role Assignments

```bash
# List all assignments in a resource group
az role assignment list \
  --resource-group my-rg-dev \
  --output table

# Find all assignments for a specific principal
az role assignment list \
  --assignee "<object-id-or-app-id>" \
  --all \
  --output table

# List assignments scoped to subscription (should be minimal)
az role assignment list \
  --scope "/subscriptions/<subscription-id>" \
  --output table
```

---

## Anti-Patterns

| Anti-Pattern | Why Wrong | Fix |
|--------------|-----------|-----|
| Assign `Owner` to CI/CD pipeline | CI/CD can modify IAM — blast radius too wide | Use `Contributor` scoped to resource group |
| Assign `Contributor` at subscription level | Affects all resource groups including prod | Scope to specific resource group |
| Use `az ad sp create-for-rbac --role Contributor` default | Assigns Contributor at subscription scope | Always `--skip-assignment`, then assign manually |
| Share one SP across environments | Dev compromise affects prod | One SP per environment |
| Never audit `az role assignment list` | Stale permissions accumulate | Audit quarterly minimum |

---

## See Also

- [Azure Destructive Operations](../concepts/azure-destructive-operations.md)
- [Safe Azure Operations](../patterns/safe-azure-operations.md)
- [Quick Reference](../quick-reference.md)
