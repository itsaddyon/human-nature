const { execSync } = require('child_process');
const path = require('path');

const REPO = '/home/itsaddyon/.openclaw/workspace/main/human-nature';

// Delegate to daily-append.py for validation and consistent processing
try {
  execSync('python3 daily-append.py --check', {
    cwd: REPO,
    stdio: 'inherit'
  });
} catch (e) {
  process.exit(1);
}
