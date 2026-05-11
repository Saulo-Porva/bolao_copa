#!/usr/bin/env node
'use strict';

// Multi-cloud destructive operation guard — GCP + AWS + Azure.
// Blocks irreversible commands and any command targeting production environments.
const DANGER_RULES = [
  // ── GCP ───────────────────────────────────────────────────────────────────
  { pattern: /--project[= ][\w-]*prod[\w-]*/i,          label: 'GCP PROD project', detail: 'Commands targeting prod GCP projects require explicit confirmation.' },
  { pattern: /gcloud\s+run\s+services?\s+delete/i,       label: 'gcloud run services delete', detail: 'Deletes a Cloud Run service immediately.' },
  { pattern: /gcloud\s+storage\s+rm\b.*--recursive/i,   label: 'gcloud storage rm --recursive', detail: 'Recursively deletes GCS objects — irreversible.' },
  { pattern: /gcloud\s+firestore\s+databases?\s+delete/i, label: 'gcloud firestore databases delete', detail: 'Deletes Firestore database and all data.' },
  { pattern: /gcloud\s+pubsub\s+topics?\s+delete/i,     label: 'gcloud pubsub topics delete', detail: 'Deletes Pub/Sub topic and pending messages.' },
  { pattern: /gcloud\s+projects?\s+remove-iam-policy-binding/i, label: 'gcloud remove-iam-policy-binding', detail: 'Removes IAM policy binding — may break running services.' },
  { pattern: /\bbq\s+rm\b.*-r\b/i,                      label: 'bq rm -r (recursive)', detail: 'Recursively deletes BigQuery dataset.' },
  { pattern: /terraform\s+destroy\b/i,                  label: 'terraform destroy', detail: 'Destroys all Terraform-managed infrastructure.' },
  { pattern: /terragrunt\s+destroy\b/i,                 label: 'terragrunt destroy', detail: 'Destroys all Terragrunt-managed infrastructure.' },

  // ── AWS ───────────────────────────────────────────────────────────────────
  { pattern: /--profile\s+[\w-]*(prod|production)[\w-]*/i, label: 'AWS PROD profile', detail: 'Command targets AWS production profile.' },
  { pattern: /aws\s+s3\s+(rb\b.*--force|rm\b.*--recursive)/i, label: 'aws s3 rb/rm destructive', detail: 'Removes S3 bucket or objects recursively — irreversible.' },
  { pattern: /aws\s+ec2\s+terminate-instances/i,        label: 'aws ec2 terminate-instances', detail: 'Permanently terminates EC2 instances.' },
  { pattern: /aws\s+rds\s+(delete-db-instance|delete-db-cluster)\b/i, label: 'aws rds delete', detail: 'Deletes RDS/Aurora database.' },
  { pattern: /aws\s+lambda\s+delete-function/i,         label: 'aws lambda delete-function', detail: 'Removes Lambda function permanently.' },
  { pattern: /aws\s+iam\s+(delete-role|delete-user|delete-policy)\b/i, label: 'aws iam delete', detail: 'Removes IAM identities — may break services immediately.' },
  { pattern: /aws\s+cloudformation\s+delete-stack/i,    label: 'aws cloudformation delete-stack', detail: 'Destroys entire CloudFormation stack and all its resources.' },
  { pattern: /aws\s+eks\s+delete-cluster/i,             label: 'aws eks delete-cluster', detail: 'Deletes EKS Kubernetes cluster.' },

  // ── Azure ──────────────────────────────────────────────────────────────────
  { pattern: /--resource-group\s+[\w-]*(prod|production)[\w-]*/i, label: 'Azure PROD resource group', detail: 'Command targets Azure production resource group.' },
  { pattern: /az\s+group\s+delete/i,                    label: 'az group delete', detail: 'Deletes Azure resource group — removes all resources in the group.' },
  { pattern: /az\s+(vm|vmss)\s+delete/i,                label: 'az vm delete', detail: 'Deletes Azure Virtual Machine.' },
  { pattern: /az\s+storage\s+account\s+delete/i,        label: 'az storage account delete', detail: 'Removes Azure storage account and all data.' },
  { pattern: /az\s+functionapp\s+delete/i,              label: 'az functionapp delete', detail: 'Deletes Azure Function App.' },
  { pattern: /az\s+aks\s+delete/i,                      label: 'az aks delete', detail: 'Deletes AKS Kubernetes cluster.' },
  { pattern: /az\s+keyvault\s+delete/i,                 label: 'az keyvault delete', detail: 'Deletes Azure Key Vault — secrets and keys become inaccessible.' },
  { pattern: /az\s+sql\s+(server|db)\s+delete/i,        label: 'az sql delete', detail: 'Deletes Azure SQL database or server.' },
];

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(raw);
    if (data.tool_name !== 'Bash') process.exit(0);
    const command = String(data.tool_input?.command || '');
    for (const { pattern, label, detail } of DANGER_RULES) {
      if (pattern.test(command)) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `🚨 Destructive operation blocked: ${label}\n\n${detail}\n\nCommand:\n  ${command.slice(0, 300)}\n\nTo proceed, confirm explicitly in the next prompt.`,
        }));
        process.exit(0);
      }
    }
  } catch {}
  process.exit(0);
});
