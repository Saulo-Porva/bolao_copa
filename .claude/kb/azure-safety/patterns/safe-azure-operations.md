# Safe Azure Operations Pattern

> **Purpose**: Safe CLI patterns for common Azure operations — inspect before act, stop before delete
> **MCP Validated**: 2026-05-08

## When to Use

- You need to modify or remove Azure resources without triggering the safety hook
- You want to verify resource state before making changes
- You are scripting automation that should fail safe rather than destructively

---

## Resource Groups

### Safe: Inspect before touching

```bash
# List all resource groups with location and tags
az group list --output table

# Show a specific group and its metadata
az group show --name my-rg --output json

# List all resources inside a group
az resource list --resource-group my-rg --output table
```

### Safe: Lock a resource group to prevent accidental deletion

```bash
# Create a delete lock (blocks az group delete and az resource delete)
az lock create \
  --name "protect-prod" \
  --resource-group my-rg-prod \
  --lock-type CanNotDelete

# List existing locks
az lock list --resource-group my-rg-prod --output table
```

---

## Virtual Machines

### Safe: Stop billing without deletion

```bash
# Deallocate VM — stops billing for compute, preserves disk data
az vm deallocate \
  --resource-group my-rg-dev \
  --name my-vm

# Verify state
az vm show \
  --resource-group my-rg-dev \
  --name my-vm \
  --query "powerState"
```

### Safe: Snapshot disk before any risky operation

```bash
# Get disk ID
DISK_ID=$(az vm show \
  --resource-group my-rg-dev \
  --name my-vm \
  --query "storageProfile.osDisk.managedDisk.id" \
  --output tsv)

# Create snapshot
az snapshot create \
  --resource-group my-rg-dev \
  --name my-vm-os-backup \
  --source "$DISK_ID"
```

---

## Storage Accounts

### Safe: Inspect before modifying

```bash
# List accounts and their replication config
az storage account list \
  --resource-group my-rg-dev \
  --output table

# Check soft-delete settings on a specific account
az storage blob service-properties delete-policy show \
  --account-name mystoragedev \
  --auth-mode login
```

### Safe: Enable soft-delete to protect blobs

```bash
# Enable blob soft-delete with 14-day retention
az storage blob service-properties delete-policy update \
  --account-name mystoragedev \
  --enable true \
  --days-retained 14 \
  --auth-mode login
```

### Safe: Revoke public access instead of deleting

```bash
# Disable public blob access
az storage account update \
  --name mystoragedev \
  --resource-group my-rg-dev \
  --allow-blob-public-access false
```

---

## Function Apps

### Safe: Stop without deleting

```bash
# Stop a function app (keeps config, no billing for executions)
az functionapp stop \
  --resource-group my-rg-dev \
  --name my-func-dev

# Restart
az functionapp start \
  --resource-group my-rg-dev \
  --name my-func-dev
```

### Safe: Export settings before any change

```bash
# Export all app settings to a file for backup
az functionapp config appsettings list \
  --resource-group my-rg-dev \
  --name my-func-dev \
  --output json > appsettings_backup.json
```

---

## AKS Clusters

### Safe: Stop cluster to pause billing

```bash
# Stop cluster — preserves node pool config and Kubernetes state
az aks stop \
  --resource-group my-rg-dev \
  --name my-aks-dev

# Resume
az aks start \
  --resource-group my-rg-dev \
  --name my-aks-dev
```

### Safe: Cordon and drain before node changes

```bash
# Cordon node (prevents new pod scheduling)
kubectl cordon <node-name>

# Drain node (evicts pods gracefully with 120s timeout)
kubectl drain <node-name> \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --grace-period=120
```

---

## Key Vault

### Safe: Revoke access instead of deleting

```bash
# Remove a specific principal's access policy
az keyvault delete-policy \
  --name my-keyvault-dev \
  --object-id <principal-object-id>

# Disable a secret without deleting the vault
az keyvault secret set-attributes \
  --vault-name my-keyvault-dev \
  --name my-secret \
  --enabled false
```

### Safe: Enable soft-delete and purge protection

```bash
# Verify soft-delete status (should be true for all vaults)
az keyvault show \
  --name my-keyvault-dev \
  --query "properties.enableSoftDelete"

# Enable purge protection (prevents permanent deletion during retention window)
az keyvault update \
  --name my-keyvault-dev \
  --resource-group my-rg-dev \
  --enable-purge-protection true
```

---

## SQL Databases

### Safe: Export before modification

```bash
# Export database to a BACPAC file in storage
az sql db export \
  --resource-group my-rg-dev \
  --server my-sql-server-dev \
  --name my-database \
  --storage-key-type StorageAccessKey \
  --storage-key "$STORAGE_KEY" \
  --storage-uri "https://mystoragedev.blob.core.windows.net/backups/mydb.bacpac" \
  --admin-user sqladmin \
  --admin-password "$SQL_ADMIN_PASSWORD"
```

### Safe: Check existing backups before any schema change

```bash
# List available point-in-time restore points
az sql db list-deleted \
  --resource-group my-rg-dev \
  --server my-sql-server-dev

# Show retention policy
az sql db show \
  --resource-group my-rg-dev \
  --server my-sql-server-dev \
  --name my-database \
  --query "requestedBackupStorageRedundancy"
```

---

## See Also

- [Azure Destructive Operations](../concepts/azure-destructive-operations.md)
- [Azure Least Privilege](../patterns/azure-least-privilege.md)
- [Quick Reference](../quick-reference.md)
