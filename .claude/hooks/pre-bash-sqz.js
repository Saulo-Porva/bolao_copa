#!/usr/bin/env node
'use strict';

/**
 * PreToolUse hook — compresses Bash outputs via sqz before they reach Claude.
 *
 * Mechanism: rewrites the bash command to pipe through "sqz compress",
 * so Claude only sees the compressed output (real token savings — not just
 * a post-processing systemMessage).
 *
 * Toggle: .claude/.sqz-on file controls the mode.
 *   exists  → compression ON  (default for daily work)
 *   missing → debug mode      (full output, nothing lost)
 *
 * Exempt commands always run with full output regardless of toggle:
 *   - bq query / bq show   (data rows need fidelity)
 *   - gcloud firestore      (document inspection)
 *   - python -m pytest      (exact test results)
 *   - ruff                  (exact lint messages)
 *   - Short commands        (< threshold: no gain)
 */

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FLAG_FILE = path.join(__dirname, '..', '.sqz-on');
const SQZ_BIN = path.join(__dirname, '..', '..', 'tools', 'bin', 'sqz.exe');

// Commands where full output is required — compression disabled regardless of toggle
const EXEMPT_PATTERNS = [
  /\bbq\s+(query|show|head|ls)\b/i,        // BigQuery data rows
  /gcloud\s+firestore/i,                    // Firestore documents
  /python\s+-m\s+pytest/i,                  // Test results
  /\bpytest\b/i,                            // Test results
  /\bruff\s+(check|format)/i,               // Lint output
  /gcloud\s+secrets?\s+(versions?\s+access|describe)/i, // Secrets — never compress
];

function isExempt(command) {
  return EXEMPT_PATTERNS.some(p => p.test(command));
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    // Debug mode: flag file absent → full output
    if (!fs.existsSync(FLAG_FILE)) process.exit(0);

    // sqz binary must exist
    if (!fs.existsSync(SQZ_BIN)) process.exit(0);

    const data = JSON.parse(raw);
    if (data.tool_name !== 'Bash') process.exit(0);

    const command = String(data.tool_input?.command || '');

    // Exempt commands always get full output
    if (isExempt(command)) process.exit(0);

    // Delegate to sqz — it rewrites the command to pipe through sqz compress
    const result = spawnSync(SQZ_BIN, ['hook', 'claude'], {
      input: raw,
      encoding: 'utf8',
      timeout: 5000,
    });

    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
    process.exit(result.status || 0);

  } catch {
    // Any failure = silent passthrough, never block Claude
    process.exit(0);
  }
});
