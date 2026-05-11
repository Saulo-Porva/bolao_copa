#!/usr/bin/env node
'use strict';

// Blocks Bash commands that appear to pass hardcoded secrets inline.
const LEAK_COMMANDS = /\b(echo|printf|curl|wget|export|set\s+\w|env\s|printenv)\b/i;

const SECRET_PATTERNS = [
  { pattern: /AKIA[0-9A-Z]{16}/,                                          label: 'AWS Access Key ID' },
  { pattern: /(?<![A-Za-z0-9])[A-Za-z0-9/+]{40}(?![A-Za-z0-9/+])/,      label: 'possible AWS Secret Key (40 chars base64)' },
  { pattern: /ghp_[a-zA-Z0-9]{36}/,                                        label: 'GitHub Personal Access Token' },
  { pattern: /github_pat_[a-zA-Z0-9_]{82}/,                                label: 'GitHub Fine-grained Token' },
  { pattern: /sk-[a-zA-Z0-9]{48}/,                                         label: 'OpenAI API Key' },
  { pattern: /AIza[0-9A-Za-z\-_]{35}/,                                     label: 'Google API Key' },
  { pattern: /-----BEGIN\s+(RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY/,        label: 'Private Key' },
  { pattern: /xox[baprs]-[0-9A-Za-z\-]{10,}/,                             label: 'Slack Token' },
  { pattern: /SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}/,               label: 'SendGrid API Key' },
  { pattern: /re_[a-zA-Z0-9]{32}/,                                         label: 'Resend API Key' },
  { pattern: /sk-ant-[a-zA-Z0-9\-_]{90,}/,                                 label: 'Anthropic API Key' },
  { pattern: /Bearer\s+[A-Za-z0-9\-_]{20,}/,                              label: 'Bearer token inline in command' },
];

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(raw);
    if (data.tool_name !== 'Bash') process.exit(0);
    const command = String(data.tool_input?.command || '');
    if (!LEAK_COMMANDS.test(command)) process.exit(0);
    for (const { pattern, label } of SECRET_PATTERNS) {
      if (pattern.test(command)) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `🔑 Possible secret detected in command: ${label}\n\nNever pass secrets directly in commands.\nUse: Secret Manager (GCP), AWS Secrets Manager, Azure Key Vault, or environment variables set outside Claude.\n\nCommand:\n  ${command.slice(0, 200)}`,
        }));
        process.exit(0);
      }
    }
  } catch {}
  process.exit(0);
});
