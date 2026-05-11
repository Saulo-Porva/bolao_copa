# AWS Safety Quick Reference

> Blocked vs safe commands at a glance. For full context, see linked files.
> **MCP Validated**: 2026-05-08

## Blocked Commands (Hook Will Abort)

| Blocked Command | Safe Alternative |
|-----------------|-----------------|
| `aws s3 rb --force s3://bucket` | `aws s3 ls s3://bucket` (inspect first) |
| `aws s3 rm --recursive s3://bucket/prefix` | `aws s3 ls s3://bucket/prefix` (list, then delete specific keys) |
| `aws ec2 terminate-instances --instance-ids i-xxx` | `aws ec2 stop-instances --instance-ids i-xxx` |
| `aws rds delete-db-instance --db-instance-identifier mydb` | `aws rds describe-db-instances` |
| `aws rds delete-db-cluster --db-cluster-identifier mycluster` | `aws rds describe-db-clusters` |
| `aws lambda delete-function --function-name my-fn` | `aws lambda get-function --function-name my-fn` |
| `aws iam delete-role --role-name my-role` | `aws iam get-role --role-name my-role` |
| `aws iam delete-user --user-name my-user` | `aws iam get-user --user-name my-user` |
| `aws iam delete-policy --policy-arn arn:aws:iam::...` | `aws iam get-policy --policy-arn arn:aws:iam::...` |
| `aws cloudformation delete-stack --stack-name my-stack` | `aws cloudformation describe-stacks --stack-name my-stack` |
| `aws eks delete-cluster --name my-cluster` | `aws eks describe-cluster --name my-cluster` |
| `aws ... --profile prod ...` | Use `--profile dev` profile only |
| `aws ... --profile production ...` | Use `--profile dev` profile only |

## Profile Rules

| Profile | When to Use | Risk Level |
|---------|-------------|------------|
| `--profile dev` | Default for all operations | Low |
| `--profile staging` | Requires explicit confirmation | Medium |
| `--profile prod` | BLOCKED by hook | Critical |
| `--profile production` | BLOCKED by hook | Critical |

## Safe Read-Only Commands (Always OK)

| Purpose | Command |
|---------|---------|
| List S3 buckets | `aws s3 ls` |
| List S3 objects | `aws s3 ls s3://bucket/prefix/` |
| Describe EC2 instances | `aws ec2 describe-instances` |
| Describe RDS instances | `aws rds describe-db-instances` |
| List Lambda functions | `aws lambda list-functions` |
| List IAM roles | `aws iam list-roles` |
| Describe CloudFormation stacks | `aws cloudformation describe-stacks` |
| Describe EKS clusters | `aws eks describe-cluster --name x` |

## IAM Roles (Least Privilege)

| Task | Role / Policy |
|------|--------------|
| Read S3 objects | `s3:GetObject` on specific bucket ARN |
| Write S3 objects | `s3:PutObject` on specific bucket ARN |
| Invoke Lambda | `lambda:InvokeFunction` on specific function ARN |
| Read DynamoDB | `dynamodb:GetItem`, `dynamodb:Query` on specific table |
| Publish SNS | `sns:Publish` on specific topic ARN |
| Send SQS messages | `sqs:SendMessage` on specific queue ARN |

## Related Documentation

| Topic | Path |
|-------|------|
| Destructive operations explained | `concepts/aws-destructive-operations.md` |
| Safe S3 patterns | `patterns/safe-s3-operations.md` |
| Safe EC2 patterns | `patterns/safe-ec2-operations.md` |
| IAM least privilege | `patterns/iam-least-privilege.md` |
| Full Index | `index.md` |
