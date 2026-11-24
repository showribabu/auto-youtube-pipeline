#!/usr/bin/env node
/**
 * Auto YouTube Pipeline — GitHub Setup (CommonJS for compatibility)
 * Prerequisites: @octokit/rest installed locally
 */

const { Octokit } = require('@octokit/rest');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(r => rl.question(q, r));

async function main() {
  console.log('\n═══════════════════════════════════════════');
  console.log(' Auto YouTube Pipeline — GitHub Setup');
  console.log('═══════════════════════════════════════════\n');

  const username = 'rajubai6419';
  const repoName = 'auto-youtube-pipeline';

  // Get token
  let octokit;
  try {
    octokit = new Octokit({ auth: process.env.GH_TOKEN });
    const { data: user } = await octokit.users.getAuthenticated();
    console.log(`✓ Authenticated as: ${user.login}\n`);
  } catch (e) {
    console.log('Step 1: Authenticate with GitHub...');
    console.log('Go to: https://github.com/settings/tokens/new');
    console.log('  Token name: auto-youtube-pipeline');
    console.log('  Expiration: 90 days');
    console.log('  Scopes: repo, workflow\n');
    // Fallback: read from env or require manual step
    const token = (process.env.GH_TOKEN || '').trim();
    if (!token) {
      console.log('\nPlease provide a GitHub Personal Access Token with repo + workflow scopes.');
      console.log('Go to: https://github.com/settings/tokens/new');
      console.log('Then re-run with: GH_TOKEN=your_token_here node deploy/github_auth.cjs\n');
      rl.close();
      process.exit(1);
    }
    octokit = new Octokit({ auth: token });
    try {
      const { data: user } = await octokit.users.getAuthenticated();
      console.log(`✓ Authenticated as: ${user.login}\n`);
    } catch (e2) {
      console.error('✗ Invalid token:', e2.message);
      process.exit(1);
    }
  }

  // Create or check repo
  try {
    await octokit.repos.get({ owner: username, repo: repoName });
    console.log(`✓ Repository exists: https://github.com/${username}/${repoName}\n`);
  } catch (e) {
    if (e.status === 404) {
      console.log('Creating repository...');
      await octokit.repos.createForAuthenticatedUser({
        name: repoName,
        description: 'Auto AI Video Generation & YouTube Upload Pipeline',
        private: false,
        auto_init: true,
      });
      console.log(`✓ Created: https://github.com/${username}/${repoName}\n`);
    } else throw e;
  }

  // Upload files
  const PROJECT_ROOT = process.cwd();
  console.log('Uploading files...\n');

  const ignoreDirs = ['__pycache__', '.git', '.venv', 'node_modules', 'output', 'logs', 'cache'];
  const ignoreExt = ['.pyc', '.db', '.log'];
  let count = 0;

  async function walkDir(dir, githubPath) {
    const entries = await fs.promises.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const ghEntry = githubPath ? `${githubPath}/${entry.name}` : entry.name;

      if (entry.isDirectory()) {
        if (ignoreDirs.includes(entry.name)) continue;
        await walkDir(fullPath, ghEntry);
      } else if (entry.isFile()) {
        if (ignoreExt.some(ext => entry.name.endsWith(ext))) continue;
        try {
          const content = await fs.promises.readFile(fullPath);
          let sha = undefined;
          try {
            const existing = await octokit.repos.getContent({ owner: username, repo: repoName, path: ghEntry });
            sha = existing.data.sha;
          } catch {}
          await octokit.repos.createOrUpdateFileContents({
            owner: username,
            repo: repoName,
            path: ghEntry,
            message: `Add ${entry.name}`,
            content: Buffer.from(content).toString('base64'),
            sha,
          });
          console.log(`  ✓ ${ghEntry}`);
          count++;
        } catch (e) {
          if (e.status !== 422 && e.status !== 409) {
            console.warn(`  ✗ ${ghEntry}: ${e.message}`);
          }
        }
      }
    }
  }

  await walkDir(PROJECT_ROOT, '');
  console.log(`\n✓ Uploaded ${count} files!\n`);

  // Update daily.yml workflow
  const workflowContent = `name: Daily YouTube Pipeline

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  daily-run:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: sudo apt-get update && sudo apt-get install -y ffmpeg fonts-dejavu-core
      - run: |
          python -m venv venv
          source venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
      - run: sudo cp -r assets/dejavu-fonts-ttf-2.37/ttf/*.ttf /usr/share/fonts/truetype/dejavu/ && sudo fc-cache -fv
      - run: |
          source venv/bin/activate
          cd scripts
          python test_pipeline.py
`;

  try {
    const existing = await octokit.repos.getContent({ owner: username, repo: repoName, path: '.github/workflows/daily.yml' });
    await octokit.repos.createOrUpdateFileContents({
      owner: username,
      repo: repoName,
      path: '.github/workflows/daily.yml',
      message: 'Update daily workflow config',
      content: Buffer.from(workflowContent).toString('base64'),
      sha: existing.data.sha,
    });
    console.log('✓ Updated daily.yml workflow\n');
  } catch (e) {
    console.warn('  Note: Could not update workflow file:', e.message);
  }

  console.log('═══════════════════════════════════════════');
  console.log(' SETUP COMPLETE!\n');
  console.log(`Repository: https://github.com/${username}/${repoName}`);
  console.log('\nNext steps:');
  console.log('1. Go to: https://github.com/' + username + '/' + repoName + '/settings/secrets/actions');
  console.log('   Add these secrets:');
  console.log('   - YOUTUBE_REFRESH_TOKEN: [from Google OAuth]');
  console.log('   - GOOGLE_CLIENT_ID: [from Google Cloud Console]');
  console.log('   - GOOGLE_CLIENT_SECRET: [from Google Cloud Console]');
  console.log('\n2. Enable workflows: Settings → Actions → General → Allow all actions');
  console.log('3. Trigger: Actions tab → "Daily YouTube Pipeline" → Run workflow');
  console.log('═══════════════════════════════════════════\n');

  rl.close();
}

main().catch(e => { console.error(e); process.exit(1); });
