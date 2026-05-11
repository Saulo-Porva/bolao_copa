#!/usr/bin/env node
'use strict';

/**
 * PreToolUse hook — blocks destructive Bash commands before execution.
 *
 * Covers GCP prod deletions, BigQuery drops, Terraform destroy,
 * and filesystem rm -rf on paths that matter.
 *
 * Exit 0 = allow. JSON { decision: "block", reason: "..." } = block.
 */

const DANGER_RULES = [
  // GCP prod project operations
  {
    pattern: /--project[= ][\w-]*prod[\w-]*/i,
    label: 'operação em projeto GCP de PRODUÇÃO',
    detail: 'Operações em projetos prod requerem confirmação explícita.',
  },
  // Cloud Run delete
  {
    pattern: /gcloud\s+run\s+services?\s+delete/i,
    label: 'gcloud run services delete',
    detail: 'Deletar um Cloud Run service derruba o endpoint imediatamente.',
  },
  // GCS rm recursive
  {
    pattern: /gcloud\s+storage\s+rm\b.*--recursive/i,
    label: 'gcloud storage rm --recursive',
    detail: 'Remoção recursiva de bucket/prefixo é irreversível.',
  },
  // Firestore delete/clear
  {
    pattern: /gcloud\s+firestore\s+(databases?\s+delete|bulk-delete|documents?\s+delete)/i,
    label: 'Firestore delete',
    detail: 'Dados do Firestore não têm recycle bin.',
  },
  // Pub/Sub delete
  {
    pattern: /gcloud\s+pubsub\s+(topics?|subscriptions?)\s+delete/i,
    label: 'Pub/Sub resource deletion',
    detail: 'Deletar topics/subscriptions interrompe o pipeline de mensagens.',
  },
  // BigQuery
  {
    pattern: /bq\s+rm\b/i,
    label: 'bq rm — remoção BigQuery',
    detail: 'Tabelas/datasets removidos com bq rm não são recuperáveis sem backup.',
  },
  {
    pattern: /DROP\s+(TABLE|DATASET|SCHEMA)\b/i,
    label: 'SQL DROP TABLE / DATASET',
    detail: 'DDL destrutivo no BigQuery.',
  },
  // Terraform / Terragrunt destroy
  {
    pattern: /\b(terraform|terragrunt)\s+destroy\b/i,
    label: 'terraform/terragrunt destroy',
    detail: 'Destrói recursos de infra provisionados. Verifique o target antes de confirmar.',
  },
  // Cloud Build delete
  {
    pattern: /gcloud\s+builds?\s+cancel|gcloud\s+artifacts?\s+.*delete/i,
    label: 'deleção de build/artifact',
    detail: 'Artifacts deletados afetam rollback e auditoria.',
  },
  // IAM binding remove — pode quebrar serviços
  {
    pattern: /gcloud\s+projects?\s+remove-iam-policy-binding/i,
    label: 'remoção de IAM binding',
    detail: 'Remover roles de SA pode derrubar funções imediatamente.',
  },
  // Filesystem rm -rf on non-tmp paths
  {
    pattern: /rm\s+-[rf]{1,2}f?\s+(\/(?!tmp)[^\s]+|[A-Z]:\\)/i,
    label: 'rm -rf em caminho permanente',
    detail: 'Remoção recursiva fora de /tmp.',
  },
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
          reason:
            `🚨 Operação destrutiva bloqueada: ${label}\n\n` +
            `${detail}\n\n` +
            `Comando detectado:\n  ${command.slice(0, 300)}\n\n` +
            `Para prosseguir, confirme explicitamente no próximo prompt.`,
        }));
        process.exit(0);
      }
    }
  } catch {}
  process.exit(0);
});
