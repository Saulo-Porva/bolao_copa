#!/usr/bin/env node
'use strict';

// Stop hook — blocks Claude from stopping if tests fail or TODOs remain in modified files.
// Never blocks on its own errors: unknown → allow.
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TIMEOUT_MS = 30_000;

function runSync(cmd, args, opts = {}) {
  return spawnSync(cmd, args, {
    encoding: 'utf8',
    timeout: opts.timeout || TIMEOUT_MS,
    cwd: opts.cwd || process.cwd(),
    shell: true,
  });
}

function getModifiedFiles(cwd) {
  const r = runSync('git', ['diff', '--name-only', 'HEAD'], { cwd, timeout: 5_000 });
  if (r.status !== 0 || !r.stdout) return [];
  return r.stdout.trim().split('\n').filter(Boolean);
}

function runPytest(cwd) {
  const r = runSync('python', ['-m', 'pytest', '--tb=no', '-q', '--no-header'], { cwd, timeout: TIMEOUT_MS });
  if (r.status === null) return null;  // timeout → don't block
  if (r.status === 0) return null;     // all pass
  const match = (r.stdout || '').match(/(\d+)\s+failed/);
  return match ? `${match[1]} test(s) failing` : 'tests failing (run pytest to see details)';
}

function findTodos(cwd, files) {
  const relevant = files.filter(f => /\.(py|js|ts)$/.test(f));
  if (!relevant.length) return null;
  const found = [];
  for (const f of relevant) {
    try {
      const lines = fs.readFileSync(path.join(cwd, f), 'utf8').split('\n');
      lines.forEach((line, i) => {
        if (/\b(TODO|FIXME)\b/.test(line)) found.push(`${f}:${i + 1} — ${line.trim().slice(0, 80)}`);
      });
    } catch {}
  }
  return found.length ? found.slice(0, 5).join('\n') : null;
}

function checkSddGap(cwd) {
  try {
    const featuresDir = path.join(cwd, '.claude', 'sdd', 'features');
    const reportsDir  = path.join(cwd, '.claude', 'sdd', 'reports');
    if (!fs.existsSync(featuresDir)) return null;
    const designs = fs.readdirSync(featuresDir).filter(f => f.startsWith('DESIGN_'));
    const reports = fs.existsSync(reportsDir) ? fs.readdirSync(reportsDir) : [];
    const missing = designs.filter(d => {
      const name = d.replace('DESIGN_', '').replace('.md', '');
      return !reports.some(r => r.includes(name));
    });
    return missing.length ? `SDD: ${missing.length} DESIGN(s) without BUILD_REPORT — remember /ship when done` : null;
  } catch { return null; }
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(raw);
    const cwd  = data.cwd || process.cwd();

    if (data.stop_reason === 'user_interrupted') process.exit(0);

    const modified = getModifiedFiles(cwd);
    if (!modified.length) process.exit(0);

    if (modified.some(f => f.endsWith('.py'))) {
      const fail = runPytest(cwd);
      if (fail) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `🔴 Stop blocked: ${fail}`,
          hookSpecificOutput: { hookEventName: 'Stop', additionalContext: 'Fix failing tests before stopping. Run: python -m pytest -v' },
        }));
        process.exit(0);
      }
    }

    const todos = findTodos(cwd, modified);
    if (todos) {
      process.stdout.write(JSON.stringify({
        decision: 'block',
        reason: `📝 Stop blocked: TODO/FIXME found in modified files:\n${todos}`,
        hookSpecificOutput: { hookEventName: 'Stop', additionalContext: 'Resolve TODOs or remove them if not applicable.' },
      }));
      process.exit(0);
    }

    const sddWarn = checkSddGap(cwd);
    if (sddWarn) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: { hookEventName: 'Stop', additionalContext: `⚠️ ${sddWarn}` },
      }));
    }
  } catch {}
  process.exit(0);
});
