# Azure Safety Quick Reference

> Fast lookup for blocked vs safe commands. For details, see linked concept/pattern files.
> **MCP Validated**: 2026-05-08

## Hook-Blocked Commands (never run without explicit confirmation)

| Command | Why Blocked |
|---------|-------------|
| `az group delete --name ...` | Deletes entire resource group and all its resources |
| `az vm delete --name ...` | Permanently destroys a virtual machine |
| `az vmss delete --name ...` | Destroys entire VM scale set |
| `az storage account delete --name ...` | Deletes storage account and all blobs |
| `az functionapp delete --name ...` | Removes function app and its configuration |
| `az aks delete --name ...` | Destroys Kubernetes cluster and node pools |
| `az keyvault delete --name ...` | Deletes vault (recoverable only if soft-delete on) |
| `az sql server delete --name ...` | Removes SQL server and all databases |
| `az sql db delete --name ...` | Permanently drops a database |
| `... --resource-group *-prod*` | Any command targeting a prod resource group |
| `... --resource-group *-production*` | Any command targeting a production resource group |

## Safe Alternatives

| Instead of | Use |
|------------|-----|
| `az group delete` | `az group show` to inspect, then ask user |
| `az vm delete` | `az vm deallocate` to stop billing without deletion |
| `az storage account delete` | `az storage account show` to audit first |
| `az functionapp delete` | `az functionapp stop` to disable temporarily |
| `az aks delete` | `az aks stop` to pause cluster (preserves config) |
| `az keyvault delete` | `az keyvault set-policy` to revoke access instead |

## Environment Naming Convention

| Suffix | Environment | Hook Blocks? |
|--------|-------------|--------------|
| `-dev` | Development | No |
| `-staging` | Staging | No |
| `-prod` / `-production` | Production | Yes — any command |

## RBAC Quick Lookup

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| `Reader` | List, read resources | Create, modify, delete |
| `Contributor` | Create and modify | Assign roles, delete resource groups |
| `Owner` | Everything | — (avoid on prod) |
| `Storage Blob Data Reader` | Read blobs | Write, delete blobs |
| `Storage Blob Data Contributor` | Read and write blobs | Delete storage account |
| `AcrPull` | Pull container images | Push images, delete tags |

## Inspection Commands (always safe)

```bash
az group list --output table
az resource list --resource-group my-rg --output table
az vm list --resource-group my-rg --show-details
az storage account list --resource-group my-rg
az functionapp list --resource-group my-rg
```

## Related Documentation

| Topic | Path |
|-------|------|
| Destructive operations detail | `concepts/azure-destructive-operations.md` |
| Safe operation patterns | `patterns/safe-azure-operations.md` |
| RBAC least privilege | `patterns/azure-least-privilege.md` |
| Full index | `index.md` |
