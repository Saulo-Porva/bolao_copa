# AWS Destructive Operations

> **Purpose**: What each blocked AWS operation does and why it is dangerous
> **Confidence**: 0.95
> **MCP Validated**: 2026-05-08

## Overview

The `pre-bash-cloud-safety.js` hook intercepts Bash tool calls before execution. When a command matches a blocked pattern, the hook aborts it immediately and returns an error explaining why. Understanding *what* each blocked command does helps you choose the correct safe alternative.

---

## Blocked Operations

### S3: `aws s3 rb --force`

**What it does:** Removes an S3 bucket and all its contents in one command. The `--force` flag bypasses the "bucket must be empty" safeguard.

**Why it's dangerous:** All objects, versions, and delete markers are permanently deleted. S3 does not have a recycle bin. If versioning is disabled, data is gone immediately. Even with versioning, `rb --force` removes all versions.

**Safe alternative:** List objects first, delete specific keys by hand, empty the bucket manually, then remove it only after confirmation.

---

### S3: `aws s3 rm --recursive`

**What it does:** Deletes every object under a given prefix (or the entire bucket if no prefix is specified).

**Why it's dangerous:** A typo in the prefix can wipe an entire production dataset. The command runs without prompting for confirmation. Combined with `--include` and `--exclude` wildcards, the blast radius is unpredictable.

**Safe alternative:** `aws s3 ls s3://bucket/prefix/` to inspect scope, then delete individual objects with `aws s3 rm s3://bucket/prefix/specific-key`.

---

### EC2: `aws ec2 terminate-instances`

**What it does:** Permanently destroys EC2 instances. Instance-store volumes are deleted immediately; EBS volumes may or may not be deleted depending on the `DeleteOnTermination` flag set at launch.

**Why it's dangerous:** Termination is irreversible — you cannot restart a terminated instance. Any instance-store data (ephemeral storage) is always lost. If `DeleteOnTermination=true` on root EBS, the disk is also gone.

**Safe alternative:** `aws ec2 stop-instances --instance-ids i-xxx` (reversible) to pause, or `aws ec2 describe-instances` to inspect state before acting.

---

### RDS: `aws rds delete-db-instance`

**What it does:** Deletes an RDS database instance. Can optionally create a final snapshot, but if `--skip-final-snapshot` is passed, no backup is made.

**Why it's dangerous:** Deleting the instance deletes all automated backups associated with it (after the backup retention window expires). In multi-AZ setups, both primary and standby are removed. Recovery requires restoring from a manual snapshot, which may not exist.

**Safe alternative:** `aws rds describe-db-instances` to confirm state and snapshot status. Create a manual snapshot first: `aws rds create-db-snapshot`.

---

### RDS: `aws rds delete-db-cluster`

**What it does:** Deletes an Aurora cluster and all its instances. Even more destructive than `delete-db-instance` because the entire cluster (primary + read replicas) is removed.

**Why it's dangerous:** Aurora cluster deletion removes all cluster-level automated backups. A cluster can hold terabytes of production data. Restoration requires a cluster snapshot, which must have been explicitly created.

**Safe alternative:** Verify cluster endpoints and current snapshots with `aws rds describe-db-clusters` and `aws rds describe-db-cluster-snapshots`.

---

### Lambda: `aws lambda delete-function`

**What it does:** Deletes a Lambda function and all its versions, aliases, and associated event source mappings.

**Why it's dangerous:** All published versions and aliases pointing to the function are removed. If the function is wired to SQS, Kinesis, or DynamoDB streams, those event source mappings stop processing. You lose both the code and all version history stored in Lambda.

**Safe alternative:** `aws lambda get-function --function-name my-fn` to inspect, or disable the event source mapping: `aws lambda update-event-source-mapping --uuid xxx --no-enabled`.

---

### IAM: `aws iam delete-role`

**What it does:** Deletes an IAM role. The role must have all policies detached and all instance profiles disassociated before deletion succeeds.

**Why it's dangerous:** Any EC2 instance, Lambda, ECS task, or other service using this role immediately loses permissions. Services fail silently or with AccessDenied errors. Recreating the role with the same ARN is not possible in all toolchains (Terraform state may conflict).

**Safe alternative:** `aws iam get-role --role-name my-role` and `aws iam list-attached-role-policies --role-name my-role` to understand dependencies before any removal.

---

### IAM: `aws iam delete-user`

**What it does:** Deletes an IAM user. Access keys, console passwords, MFA devices, group memberships, and inline policies are all removed.

**Why it's dangerous:** Any automation using that user's access keys breaks immediately. If the user had console access, those sessions are invalidated. There is no "soft delete" or grace period.

**Safe alternative:** Disable the user's access keys first: `aws iam update-access-key --status Inactive`. Monitor for failures before proceeding.

---

### IAM: `aws iam delete-policy`

**What it does:** Deletes a customer-managed IAM policy. All policy versions are removed. The policy ARN can be reused but any existing role/user/group attachment is severed.

**Why it's dangerous:** Roles attached to this policy lose the associated permissions instantly. Policies attached to many roles can affect dozens of services at once.

**Safe alternative:** `aws iam list-entities-for-policy --policy-arn arn:...` to enumerate all attached entities before touching the policy.

---

### CloudFormation: `aws cloudformation delete-stack`

**What it does:** Deletes a CloudFormation stack and, by default, all resources it manages (EC2, RDS, S3, Lambda, IAM roles, etc.) — unless a resource has a `DeletionPolicy: Retain` attribute.

**Why it's dangerous:** A single command can destroy an entire application tier. Resources without `DeletionPolicy: Retain` are deleted in dependency order with no confirmation. Cross-stack references become dangling after deletion.

**Safe alternative:** `aws cloudformation describe-stacks --stack-name my-stack` to inspect, then `aws cloudformation list-stack-resources --stack-name my-stack` to understand what would be destroyed.

---

### EKS: `aws eks delete-cluster`

**What it does:** Deletes an EKS control plane. Node groups and Fargate profiles must be deleted first; the API server, etcd, and all Kubernetes state hosted by AWS are permanently removed.

**Why it's dangerous:** All Kubernetes workloads lose their control plane. Persistent volumes (EBS) may or may not be deleted depending on StorageClass `reclaimPolicy`. Any Route53 records or load balancers created by the cluster remain as orphans.

**Safe alternative:** `aws eks describe-cluster --name my-cluster` to inspect status. Cordon and drain nodes before any action: `kubectl cordon` and `kubectl drain`.

---

## Summary Table

| Command | Resource Lost | Reversible? | Backup Required First |
|---------|--------------|-------------|----------------------|
| `s3 rb --force` | All objects in bucket | No | Yes (manual copy) |
| `s3 rm --recursive` | All objects under prefix | No | Yes |
| `ec2 terminate-instances` | Instance + instance-store | No | Snapshot or AMI |
| `rds delete-db-instance` | DB instance + auto backups | No | Manual snapshot |
| `rds delete-db-cluster` | Entire Aurora cluster | No | Cluster snapshot |
| `lambda delete-function` | All versions + aliases | No | Code backup |
| `iam delete-role` | Role + permission grants | Partial | Policy document export |
| `iam delete-user` | User + access keys | No | Key rotation plan |
| `iam delete-policy` | Policy + all attachments | Partial | Policy JSON export |
| `cloudformation delete-stack` | All stack resources | No | Resource snapshots |
| `eks delete-cluster` | Control plane + K8s state | No | etcd backup |

## Related

- [Safe S3 Operations](../patterns/safe-s3-operations.md)
- [Safe EC2 Operations](../patterns/safe-ec2-operations.md)
- [IAM Least Privilege](../patterns/iam-least-privilege.md)
