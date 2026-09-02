const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const REPO = '/home/itsaddyon/.openclaw/workspace/main/human-nature';
const DATE = new Date().toISOString().slice(0, 10);
const startDate = new Date('2026-09-02');
const today = new Date(DATE);
const DAY_NUM = Math.floor((today - startDate) / 86400000) + 1;

const htmlPath = path.join(REPO, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// A placeholder new entry — Ishita fills this in with real observations
const newEntry = `
    {
      date: '${DATE}',
      day: 'Day ${DAY_NUM}',
      category: 'Behavior',
      title: 'Observation for ${DATE}',
      text: 'A new observation for today.',
      insight: 'An insight from today.'
    }`;

const updated = html.replace(/(const entries = \[)/, `${newEntry},`);

fs.writeFileSync(htmlPath, updated);

// Commit and push
try {
  execSync(`git add index.html && git commit -m "Day ${DAY_NUM}: Daily human nature observation — ${DATE}" && git push origin master`, {
    cwd: REPO,
    stdio: 'inherit'
  });
  console.log(`✅ Committed Day ${DAY_NUM} — ${DATE}`);
} catch (e) {
  console.log('ℹ️ Nothing new to commit today, or push failed.');
}
