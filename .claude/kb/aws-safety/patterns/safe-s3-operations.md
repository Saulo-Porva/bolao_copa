# Safe S3 Operations Pattern

> **Purpose**: Perform S3 read, upload, download, and sync operations without triggering destructive commands
> **MCP Validated**: 2026-05-08

## When to Use

- Uploading deployment artifacts or data files to S3
- Downloading files from S3 for local inspection
- Syncing a local directory to S3 (one-way, without delete)
- Listing buckets or objects before any write operation
- Copying objects between prefixes or buckets

## Safe Operation Reference

### List (Always Safe)

```bash
# List all buckets in the account
aws s3 ls --profile dev

# List objects under a prefix (non-recursive)
aws s3 ls s3://my-bucket/data/

# List recursively with human-readable sizes
aws s3 ls s3://my-bucket/data/ --recursive --human-readable --summarize
```

### Download (Always Safe)

```bash
# Download a single object
aws s3 cp s3://my-bucket/data/file.json ./local/file.json --profile dev

# Download an entire prefix to a local directory
aws s3 cp s3://my-bucket/data/ ./local/data/ --recursive --profile dev

# Preview what would be downloaded (dry-run)
aws s3 sync s3://my-bucket/data/ ./local/data/ --dryrun --profile dev
```

### Upload (Safe — creates, does not delete)

```bash
# Upload a single file
aws s3 cp ./local/artifact.zip s3://my-bucket/releases/artifact.zip --profile dev

# Upload a directory (no delete — never add --delete flag)
aws s3 sync ./local/build/ s3://my-bucket/build/ --profile dev

# Upload with explicit content type
aws s3 cp ./index.html s3://my-bucket/web/index.html \
  --content-type text/html \
  --cache-control "max-age=3600" \
  --profile dev
```

### Copy Between Locations (Safe)

```bash
# Copy object to a new key (original preserved)
aws s3 cp s3://my-bucket/data/file.json s3://my-bucket/archive/2026/file.json --profile dev

# Copy entire prefix to archive prefix
aws s3 cp s3://my-bucket/data/ s3://my-bucket/archive/2026/ --recursive --profile dev
```

## What NOT to Do

```bash
# BLOCKED: Removes bucket and all contents
aws s3 rb --force s3://my-bucket

# BLOCKED: Deletes all objects under prefix
aws s3 rm --recursive s3://my-bucket/data/

# DANGEROUS: Sync with --delete removes objects in destination not present in source
aws s3 sync ./local/ s3://my-bucket/ --delete  # Never use --delete

# DANGEROUS: Targeting prod profile
aws s3 cp file.txt s3://my-bucket/file.txt --profile prod
```

## Targeted Single-Object Delete (Manual, Not Recursive)

If you genuinely need to remove a specific object — never a recursive delete — do it explicitly:

```bash
# List the exact key first to confirm it exists and is correct
aws s3 ls s3://my-bucket/tmp/stale-file.json --profile dev

# Delete only that specific object (no wildcard, no --recursive)
aws s3 rm s3://my-bucket/tmp/stale-file.json --profile dev

# Confirm deletion
aws s3 ls s3://my-bucket/tmp/stale-file.json --profile dev
# Expected: (no output)
```

## Versioned Bucket Operations

```bash
# List all versions of an object
aws s3api list-object-versions \
  --bucket my-bucket \
  --prefix data/file.json \
  --profile dev

# Restore a previous version by copying it to the current key
aws s3api copy-object \
  --bucket my-bucket \
  --copy-source my-bucket/data/file.json?versionId=xxx \
  --key data/file.json \
  --profile dev
```

## Pre-Upload Checklist

```text
Before any aws s3 sync or cp to a production bucket:
[ ] Confirmed --profile is dev (not prod/production)
[ ] No --delete flag on sync commands
[ ] Listed destination prefix to understand existing state
[ ] Verified local source path is correct
[ ] For large uploads: tested with --dryrun first
```

## See Also

- [AWS Destructive Operations](../concepts/aws-destructive-operations.md)
- [Safe EC2 Operations](../patterns/safe-ec2-operations.md)
- [IAM Least Privilege](../patterns/iam-least-privilege.md)
