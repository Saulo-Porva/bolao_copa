# Safe EC2 Operations Pattern

> **Purpose**: Manage EC2 instances safely — describe, start, stop — without triggering termination
> **MCP Validated**: 2026-05-08

## When to Use

- Inspecting instance state, type, or network configuration
- Starting stopped instances for maintenance
- Stopping running instances (reversible pause)
- Creating AMIs or EBS snapshots before any destructive action
- Troubleshooting — never terminate to "fix" a problem

## The Key Distinction

| Action | Command | Reversible? | Data Safe? |
|--------|---------|-------------|------------|
| Stop | `stop-instances` | Yes — can restart | EBS preserved |
| Hibernate | `stop-instances --hibernate` | Yes — can restart | EBS preserved, RAM to disk |
| Terminate | `terminate-instances` | **No** | Instance-store lost, EBS depends on flag |

**Rule:** Default to `stop`, never `terminate`, unless the instance was purpose-built as ephemeral and its data is replicated elsewhere.

## Safe Read Operations

```bash
# List all instances with state and type
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,Tags[?Key==`Name`].Value|[0]]' \
  --output table \
  --profile dev

# Describe a specific instance
aws ec2 describe-instances \
  --instance-ids i-0abc123def456789 \
  --profile dev

# Check instance status (system and instance reachability)
aws ec2 describe-instance-status \
  --instance-ids i-0abc123def456789 \
  --profile dev

# List EBS volumes attached to an instance
aws ec2 describe-volumes \
  --filters Name=attachment.instance-id,Values=i-0abc123def456789 \
  --profile dev
```

## Safe Start / Stop

```bash
# Stop a running instance (EBS data preserved, instance-store data lost)
aws ec2 stop-instances \
  --instance-ids i-0abc123def456789 \
  --profile dev

# Confirm stopped state before proceeding
aws ec2 wait instance-stopped \
  --instance-ids i-0abc123def456789 \
  --profile dev

# Start a stopped instance
aws ec2 start-instances \
  --instance-ids i-0abc123def456789 \
  --profile dev

# Wait for running state
aws ec2 wait instance-running \
  --instance-ids i-0abc123def456789 \
  --profile dev
```

## Create AMI Before Major Changes

Always snapshot the instance as an AMI before any risky operation (OS upgrade, config change, migration):

```bash
# Create AMI from a stopped instance (no-reboot to avoid downtime for running)
aws ec2 create-image \
  --instance-id i-0abc123def456789 \
  --name "pre-migration-backup-$(date +%Y%m%d)" \
  --no-reboot \
  --profile dev

# Confirm AMI is available before proceeding
aws ec2 describe-images \
  --owners self \
  --filters Name=name,Values="pre-migration-backup-*" \
  --query 'Images[*].[ImageId,Name,State]' \
  --output table \
  --profile dev
```

## Create EBS Snapshot

```bash
# Get the volume ID from the instance
VOLUME_ID=$(aws ec2 describe-volumes \
  --filters Name=attachment.instance-id,Values=i-0abc123def456789 \
           Name=attachment.device,Values=/dev/xvda \
  --query 'Volumes[0].VolumeId' \
  --output text \
  --profile dev)

# Create snapshot with descriptive name
aws ec2 create-snapshot \
  --volume-id "$VOLUME_ID" \
  --description "Manual backup before maintenance $(date +%Y-%m-%d)" \
  --profile dev
```

## What NOT to Do

```bash
# BLOCKED: Permanent — no undo
aws ec2 terminate-instances --instance-ids i-0abc123def456789

# DANGEROUS: Targeting prod profile
aws ec2 stop-instances --instance-ids i-xxx --profile prod

# WRONG: Using terminate when stop is sufficient
# If the instance needs to be "reset", stop it and start it again.
# Do not terminate and re-launch unless infrastructure is fully IaC-managed.
```

## Instance Lifecycle Decision Tree

```text
Problem with instance?
├─ Unresponsive / hung → stop-instances, then start-instances
├─ Need OS update → Create AMI → stop → make changes → start
├─ Scaling down → Only terminate if:
│     1. Instance is managed by IaC (Terraform / ASG)
│     2. All data is on EBS with DeletionPolicy=Retain or already backed up
│     3. Explicit confirmation from team lead
└─ Cost savings → Use stop-instances (not terminate) for dev/test instances
```

## Pre-Stop / Pre-Terminate Checklist

```text
Before stopping:
[ ] Confirmed --profile is dev (not prod/production)
[ ] Verified instance ID matches intended target
[ ] Confirmed no active user sessions (check CloudWatch)

Before terminating (if ever allowed):
[ ] EBS snapshots or AMI created and verified available
[ ] IaC (Terraform) will recreate the resource
[ ] No unique data on instance-store volumes
[ ] Team lead confirmation received
```

## See Also

- [AWS Destructive Operations](../concepts/aws-destructive-operations.md)
- [Safe S3 Operations](../patterns/safe-s3-operations.md)
- [IAM Least Privilege](../patterns/iam-least-privilege.md)
