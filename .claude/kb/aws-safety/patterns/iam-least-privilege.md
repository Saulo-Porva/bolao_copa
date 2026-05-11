# IAM Least Privilege Pattern

> **Purpose**: Grant only the minimum AWS permissions required for a task — scoped to specific resources
> **MCP Validated**: 2026-05-08

## When to Use

- Creating IAM roles for Lambda functions, EC2 instances, or ECS tasks
- Writing inline or customer-managed policies for automation
- Auditing existing roles for over-permissioned access
- Setting up CI/CD pipeline credentials

## Core Principle

Grant permissions at the narrowest scope possible:

1. **Action scope** — list only the actions the principal needs, not `*`
2. **Resource scope** — specify the exact ARN, not `*`
3. **Condition scope** — add conditions (IP, time, MFA) when applicable

## Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DescriptiveStatementId",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/uploads/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

## Common Role Templates

### Lambda Function Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/my-function:*"
    },
    {
      "Sid": "ReadSourceBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::source-bucket/*"
    },
    {
      "Sid": "WriteDestinationBucket",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::destination-bucket/processed/*"
    }
  ]
}
```

### CI/CD Pipeline Role (deploy-only, no delete)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DeployLambda",
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:PublishVersion",
        "lambda:CreateAlias",
        "lambda:UpdateAlias"
      ],
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-function"
    },
    {
      "Sid": "PushArtifacts",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::artifacts-bucket/releases/*"
    }
  ]
}
```

## AWS CLI: Role and Policy Operations

```bash
# Create a role with a trust policy for Lambda
aws iam create-role \
  --role-name my-lambda-role \
  --assume-role-policy-document file://trust-policy.json \
  --profile dev

# trust-policy.json content:
# {
#   "Version": "2012-10-17",
#   "Statement": [{
#     "Effect": "Allow",
#     "Principal": {"Service": "lambda.amazonaws.com"},
#     "Action": "sts:AssumeRole"
#   }]
# }

# Attach a managed policy
aws iam attach-role-policy \
  --role-name my-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --profile dev

# Create and attach an inline policy
aws iam put-role-policy \
  --role-name my-lambda-role \
  --policy-name S3ReadAccess \
  --policy-document file://s3-read-policy.json \
  --profile dev

# Inspect what a role can do
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/my-lambda-role \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::source-bucket/file.txt \
  --profile dev
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `"Action": "*"` | Full account access | List only required actions |
| `"Resource": "*"` | All resources | Specify exact ARNs |
| `AdministratorAccess` managed policy | Root-equivalent access | Use task-specific policies |
| One role for all services | Shared blast radius | One role per service |
| Long-lived access keys for humans | Key leakage risk | Use IAM Identity Center (SSO) |
| No MFA for console access | Account takeover risk | Enforce MFA via condition |

## Audit Existing Roles

```bash
# List all roles and their last-used date
aws iam generate-credential-report --profile dev
aws iam get-credential-report --query 'Content' --output text --profile dev | base64 -d

# List policies attached to a role
aws iam list-attached-role-policies \
  --role-name my-role \
  --profile dev

# List inline policies
aws iam list-role-policies \
  --role-name my-role \
  --profile dev

# Find all roles that have a specific managed policy attached
aws iam list-entities-for-policy \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
  --profile dev
```

## IAM Access Analyzer

Use IAM Access Analyzer to find resources with unintended external access:

```bash
# Create an analyzer for the account
aws accessanalyzer create-analyzer \
  --analyzer-name account-analyzer \
  --type ACCOUNT \
  --profile dev

# List findings (external access to resources)
aws accessanalyzer list-findings \
  --analyzer-name account-analyzer \
  --profile dev
```

## Least Privilege Checklist

```text
Before creating or updating a role:
[ ] Listed only the specific actions needed (no wildcards)
[ ] Specified exact resource ARNs (no * unless truly needed)
[ ] Added Condition block for region, VPC, or IP where applicable
[ ] One role per service — not shared across functions
[ ] No AdministratorAccess or PowerUserAccess unless explicitly approved
[ ] Validated with simulate-principal-policy before deploying
[ ] Profile is --profile dev (not prod/production)
```

## See Also

- [AWS Destructive Operations](../concepts/aws-destructive-operations.md)
- [Safe S3 Operations](../patterns/safe-s3-operations.md)
- [Safe EC2 Operations](../patterns/safe-ec2-operations.md)
