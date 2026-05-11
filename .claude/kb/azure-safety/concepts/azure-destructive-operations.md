# Azure Destructive Operations

> **Purpose**: What each hook-blocked command does, why it's dangerous, and what data is lost
> **Confidence**: 0.95
> **MCP Validated**: 2026-05-08

## Overview

Azure CLI destructive operations are irreversible by default. The `pre-bash-cloud-safety.js` hook blocks these commands because a single typo or wrong resource group name can cause permanent data loss. Recovery, when possible, requires either soft-delete configuration or a restore from backup.

---

## `az group delete`

**What it does:** Deletes the resource group container and every resource inside it — VMs, storage accounts, databases, function apps, networking, everything — in a single operation.

**Why dangerous:** There is no "undo". Azure processes deletions asynchronously; once accepted, resources begin terminating immediately. A resource group in production can contain dozens of interconnected resources.

**Data lost:** All contained resources and their data, including storage blobs, database records, Key Vault secrets, and function app code.

**Recovery:** None without prior backup. Soft-delete on individual resources does not survive resource group deletion.

---

## `az vm delete` / `az vmss delete`

**What it does:** Permanently destroys a virtual machine (or all VMs in a scale set). With `--yes` flag, skips confirmation.

**Why dangerous:** OS disk and data disks are deleted by default unless `--no-wait` + manual disk detach is performed first. Scale set deletion removes all instances simultaneously.

**Data lost:** OS disk, attached data disks (if not detached first), in-memory state, ephemeral storage.

**Recovery:** Restore from VM snapshot or managed disk backup only.

---

## `az storage account delete`

**What it does:** Permanently removes the storage account and all containers, blobs, queues, tables, and file shares within it.

**Why dangerous:** Blob soft-delete protects individual blobs only if explicitly enabled on the account before deletion. Account-level deletion bypasses all blob-level soft-delete.

**Data lost:** All blobs, containers, file shares, queues, and table data in the account.

**Recovery:** Requires Azure Backup vault with storage account backup policy configured before deletion.

---

## `az functionapp delete`

**What it does:** Removes the function app resource, its application settings (environment variables), deployment slots, and configuration.

**Why dangerous:** Application settings stored in the portal — including connection strings, API keys, and feature flags — are deleted with the app. Code in Azure Files storage may survive if the storage account is separate.

**Data lost:** App configuration, deployment history, connection strings, scaling rules, authentication settings.

**Recovery:** Redeploy from source control. Configuration must be manually restored.

---

## `az aks delete`

**What it does:** Destroys the AKS control plane and all node pools (VMs) in the cluster.

**Why dangerous:** Node pool VMs are deleted, taking all workloads with them. Persistent Volumes backed by Azure Disks are deleted by default unless the PVC reclaim policy is `Retain`. Kubernetes state (deployments, secrets, ConfigMaps) is lost with the control plane.

**Data lost:** All running workloads, cluster secrets (including TLS certs), Kubernetes secrets, and PVCs with `Delete` reclaim policy.

**Recovery:** Redeploy cluster from IaC. Restore PV data from Azure Disk snapshots if taken.

---

## `az keyvault delete`

**What it does:** Marks the Key Vault for deletion. Behavior depends on soft-delete configuration.

**Why dangerous:** With soft-delete disabled (legacy vaults), deletion is immediate and permanent. With soft-delete enabled (default since 2021), vault enters a "deleted" state for 7–90 days before permanent purge. However, secrets are inaccessible during this window, breaking any dependent service.

**Data lost:** All secrets, keys, and certificates in the vault. Services depending on vault access fail immediately.

**Recovery:** `az keyvault recover --name ...` within the retention window (soft-delete must have been enabled).

---

## `az sql server delete` / `az sql db delete`

**What it does:** `az sql server delete` removes the logical SQL server and all databases on it. `az sql db delete` drops a single database.

**Why dangerous:** SQL logical server deletion cascades to all databases. Database deletion is permanent — there is no soft-delete equivalent. Point-in-time restore requires the database to still exist.

**Data lost:** All database records, stored procedures, views, users, and backups associated with the server/database.

**Recovery:** Restore from long-term retention backup only (if configured). Point-in-time restore is unavailable after deletion.

---

## Production Resource Group Guard

**Pattern blocked:** Any command with `--resource-group` matching `*-prod*` or `*-production*`

**Why:** Even non-destructive commands on prod resource groups carry risk. A misapplied policy binding, a wrong firewall rule, or a deployment rollback can destabilize production. The hook forces explicit user confirmation for any operation in a prod environment, not just deletions.

---

## Related

- [Safe Azure Operations](../patterns/safe-azure-operations.md)
- [Azure Least Privilege](../patterns/azure-least-privilege.md)
- [Quick Reference](../quick-reference.md)
