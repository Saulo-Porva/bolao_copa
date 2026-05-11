#!/usr/bin/env node
'use strict';

/**
 * Stop hook — exibe notificação no desktop quando Claude finaliza uma tarefa.
 *
 * Útil para sessões longas com múltiplos agentes SDD (/build, /design)
 * onde o desenvolvedor pode estar em outra janela.
 *
 * Windows: toast via PowerShell + System.Windows.Forms
 * macOS:   osascript notification
 * Linux:   notify-send (se disponível)
 */

const { execSync } = require('child_process');
const os = require('os');

function getStopReason(data) {
  // Claude Code passa stop_reason ou similar
  return data?.stop_reason || data?.reason || 'Tarefa concluída';
}

function notifyWindows(title, message) {
  const escaped = message.replace(/'/g, "''").replace(/"/g, '`"');
  const ps = [
    'Add-Type -AssemblyName System.Windows.Forms',
    'Add-Type -AssemblyName System.Drawing',
    '$n = New-Object System.Windows.Forms.NotifyIcon',
    '$n.Icon = [System.Drawing.SystemIcons]::Information',
    `$n.BalloonTipTitle = '${title}'`,
    `$n.BalloonTipText = '${escaped}'`,
    '$n.Visible = $true',
    '$n.ShowBalloonTip(6000)',
    'Start-Sleep -Milliseconds 6500',
    '$n.Dispose()',
  ].join('; ');

  execSync(`powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "${ps}"`, {
    stdio: 'ignore',
    timeout: 10000,
  });
}

function notifyMac(title, message) {
  const escaped = message.replace(/"/g, '\\"');
  execSync(`osascript -e 'display notification "${escaped}" with title "${title}"'`, {
    stdio: 'ignore',
    timeout: 5000,
  });
}

function notifyLinux(title, message) {
  execSync(`notify-send "${title}" "${message}" --icon=dialog-information`, {
    stdio: 'ignore',
    timeout: 5000,
  });
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { raw += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(raw);
    const title = 'Claude Code';
    const message = getStopReason(data);
    const platform = os.platform();

    if (platform === 'win32') notifyWindows(title, message);
    else if (platform === 'darwin') notifyMac(title, message);
    else notifyLinux(title, message);
  } catch {
    // Notification failure is non-critical — never block the stop event
  }
  process.exit(0);
});
