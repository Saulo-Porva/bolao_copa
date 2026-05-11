#!/usr/bin/env node
'use strict';

/**
 * PostToolUse hook — runs ruff check + fix on Python files after Write/Edit/MultiEdit.
 *
 * Only fires for .py files inside the project. Outputs a systemMessage
 * if ruff finds issues it cannot auto-fix, so Claude can address them.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Paths to skip (generated code, migrations, __pycache__)
const SKIP_PATTERNS = [
  /[/\\]__pycache__[/\\]/,
  /[/\\]\.venv[/\\]/,
  /[/\\]migrations[/\\]/,
  /[/\\]\.git[/\\]/,
  /[/\\]archive[/\\]/,
];

function shouldSkip(filePath) {
  return SKIP_PATTERNS.some(p => p.test(filePath));
}

function findRuff(cwd) {
  // Prefer project venv ruff to avoid version mismatch
  const venvRuff = path.join(cwd, '.venv', 'Scripts', 'ruff.exe');       // Windows
  const venvRuffUnix = path.join(cwd, '.venv', 'bin', 'ruff');           // Linux/Mac
  if (fs.existsSync(venvRuff)) return `"${venvRuff}"`;
  if (fs.existsSync(venvRuffUnix)) return `"${venvRuffUnix}"`;
  return 'python -m ruff';  // fallback
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(raw);
    const toolName = data.tool_name || '';

    if (!['Write', 'Edit', 'MultiEdit'].includes(toolName)) process.exit(0);

    const filePath = data.tool_input?.file_path || '';
    if (!filePath.endsWith('.py')) process.exit(0);
    if (shouldSkip(filePath)) process.exit(0);
    if (!fs.existsSync(filePath)) process.exit(0);

    const cwd = process.cwd();
    const ruff = findRuff(cwd);

    try {
      // Auto-fix what can be fixed silently
      execSync(`${ruff} check "${filePath}" --fix --quiet`, {
        stdio: 'pipe',
        cwd,
        timeout: 10000,
      });
    } catch (fixErr) {
      // ruff exited non-zero = unfixable issues remain
      const stdout = fixErr.stdout?.toString().trim() || '';
      const stderr = fixErr.stderr?.toString().trim() || '';
      const issues = [stdout, stderr].filter(Boolean).join('\n');

      if (issues) {
        process.stdout.write(JSON.stringify({
          systemMessage: `ruff encontrou problemas não auto-corrigíveis em ${path.basename(filePath)}:\n${issues}`,
        }));
      }
    }
  } catch {}
  process.exit(0);
});
