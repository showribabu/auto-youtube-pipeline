"""
Auto YouTube Pipeline — One-Command Deployment Script
Usage: python deploy/deploy_all.py [OPTION]

Options:
  --github     Deploy to GitHub + GitHub Actions (free, no server cost)
  --render     Deploy to Render.com (free tier, always-on service)
  --fly        Deploy to Fly.io ($5 free credit, always-on container)
  --status     Show current deployment status

Prerequisites:
  pip install requests
  gh CLI installed OR GH_TOKEN set as env var
  GitHub PAT with repo scope (for --github option)
  Render/Fly auth configured (for cloud options)
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: Install requests first: pip install requests")
    sys.exit(1)

# ─── Configuration ────────────────────────────────────────
USER_NAME = "rajubai6419"
REPO_NAME = "auto-youtube-pipeline"
GITHUB_URL = f"https://github.com/{USER_NAME}/{REPO_NAME}"
BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"
DEPLOY_DIR = BASE_DIR / "deploy"


def shell(cmd, capture=True, env=None):
    """Run shell command."""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True, env=env
    )
    return result.returncode == 0, result.stdout, result.stderr


def detect_git_username():
    """Detect current Git username for repo creation."""
    ok, out, err = shell("git config user.name", True)
    return out.strip() if ok else USER_NAME


def create_github_repo(token):
    """Create GitHub repository via API."""
    print(f"Creating GitHub repository: {USER_NAME}/{REPO_NAME}...")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {
        "name": REPO_NAME,
        "description": "Auto AI Video Generation & YouTube Upload Pipeline",
        "private": False,
        "auto_init": True,
    }
    resp = requests.post(
        "https://api.github.com/user/repos",
        json=data,
        headers=headers,
        timeout=30,
    )
    if resp.status_code == 201:
        print(f"✓ Repository created: https://github.com/{USER_NAME}/{REPO_NAME}")
        return True
    elif resp.status_code == 403:
        print("⚠ Access denied. Check your GitHub token permissions.")
        return False
    elif resp.status_code == 404:
        print(f"Repository may already exist at {GITHUB_URL}")
        return True
    else:
        print(f"✗ Failed: {resp.status_code} - {resp.text[:200]}")
        return False


def upload_files_via_git(git_token):
    """Upload all project files to GitHub via git push."""
    print("\nUploading files to GitHub...")

    # Configure git
    shell(f'git remote add origin https://{git_token}@github.com/{USER_NAME}/{REPO_NAME}.git')
    shell('git branch -M main')

    # Add all non-sensitive files
    ignore_files = ['output/*', 'logs/*', 'cache/*', 'config/.env',
                    'config/yt_token.json', '.venv/', '__pycache__/', '*.mp3', '*.db']
    shell(f'git config --local core.excludesfile .gitignore')

    # Commit and push
    ok, out, err = shell('git add .')
    if not ok:
        print(f"Add failed: {err}")
        return False

    ok, out, err = shell('git commit -m "Auto YouTube Pipeline v1.0 - Ready for deployment"')
    if not ok:
        print(f"Commit failed: {err}")
        return False

    ok, out, err = shell('git push -u origin main --force')
    if ok:
        print(f"✓ Files uploaded to: {GITHUB_URL}")
        return True
    else:
        print(f"Push failed: {err}")
        return False


def create_render_service(render_api_key):
    """Deploy to Render.com (free tier)."""
    print("\nDeploying to Render.com (free tier)...")

    # Get services list
    headers = {"Authorization": f"Bearer {render_api_key}"}

    # Create static site/service (Python app)
    app_data = {
        "name": "auto-youtube-pipeline",
        "type": "web_service",
        "region": "oregon",
        "startCommand": "python scripts/pipeline.py --scheduler",
        "healthCheckPath": "/health",
        "envVars": [],
    }

    resp = requests.post(
        "https://api.render.com/v1/services",
        json=app_data,
        headers=headers,
        timeout=30,
    )

    if resp.status_code == 201:
        service = resp.json()
        url = service.get("url", "Not available")
        print(f"✓ Service deployed: {url}")
        return True
    else:
        print(f"✗ Render deployment failed: {resp.status_code}")
        print(resp.text[:500])
        return False


def create_fly_app(fly_token):
    """Deploy to Fly.io ($5 free credit)."""
    print("\nDeploying to Fly.io...")

    # This would require flyctl installed; fallback to instructions
    print("Note: Fly.io deployment requires flyctl CLI installed.")
    print("Run: curl https://fly.io/install.sh | sh")
    print("Then: fly apps create auto-youtube-pipeline")
    print("And: fly deploy --access-token=" + fly_token[:8] + "...")
    return False  # Placeholder


def show_status():
    """Show current deployment status."""
    print("\n═══════════════════════════════════════════")
    print(" Auto YouTube Pipeline — Deployment Status")
    print("═══════════════════════════════════════════\n")

    # Check local state
    env_exists = (CONFIG_DIR / ".env").exists()
    token_exists = (CONFIG_DIR / "yt_token.json").exists()
    rendered = (BASE_DIR / "render.yaml").exists() if (BASE_DIR / "render.yaml").exists() else False

    # Check GitHub
    github_ok = False
    try:
        # Try to fetch repo info
        resp = requests.get(f"https://api.github.com/repos/{USER_NAME}/{REPO_NAME}",
                          timeout=5)
        if resp.status_code == 200:
            github_ok = True
            repo = resp.json()
            branches = requests.get(repo["branches_url"].replace("{/branch}", ""),
                                  timeout=5).json()
            latest = next(iter(branches), None)
            if latest:
                print(f"✓ GitHub: {GITHUB_URL}")
                print(f"  Latest commit: {latest['commit']['sha'][:8]}")
            else:
                print(f"✓ GitHub repo exists: {GITHUB_URL}")
        else:
            print(f"⚠ GitHub repo not found ({resp.status_code})")
    except Exception as e:
        print(f"⚠ Could not check GitHub: {e}")

    print()

    # Local checks
    print("Local Checks:")
    print(f"  {'✓' if env_exists else '✗'} Config file (.env)")
    print(f"  {'✓' if token_exists else '✗'} YouTube token (yt_token.json)")

    # Docker/build
    docker_ok = os.path.exists(BASE_DIR / "Dockerfile")
    print(f"  {'✓' if docker_ok else '✗'} Docker support")

    # Requirements
    reqs_ok = os.path.exists(BASE_DIR / "requirements.txt")
    print(f"  {'✓' if reqs_ok else '✗'} Dependencies file")

    print("\n═══════════════════════════════════════════\n")


def print_next_steps():
    """Print next steps for user."""
    print("""
═══════════════════════════════════════════
 NEXT STEPS TO COMPLETE DEPLOYMENT:
═══════════════════════════════════════════

1. GENERATE GITHUB TOKEN:
   • Go to: https://github.com/settings/tokens/new
   • Token name: auto-youtube-pipeline
   • Expiration: 90 days
   • Scopes: repo, workflow
   • Copy the token (starts with ghp_xxx...)

2. GET YOUTUBE CREDENTIALS:
   • Go to: https://console.cloud.google.com/apis/credentials
   • Enable: YouTube Data API v3
   • Create OAuth Client ID (Desktop app type)
   • Download client_secret.json

3. RUN DEPLOYMENT:
   Once you have both tokens, run:

   python deploy/deploy_all.py --github \\
     --github-token YOUR_GH_TOKEN \\
     --client-id YOUR_CLIENT_ID \\
     --client-secret YOUR_CLIENT_SECRET

   Or manually:
   - Set GH_TOKEN environment variable
   - Then run the appropriate deployment command

4. MONITOR FIRST RUN:
   After deploying, watch logs:
   - GitHub: Actions tab → Daily YouTube Pipeline
   - Render: Dashboard → Logs
   - Oracle: journalctl -u auto-youtube -f

═══════════════════════════════════════════
""")


def main():
    parser = argparse.ArgumentParser(description="Auto YouTube Pipeline Deployment Tool")
    parser.add_argument("--github", action="store_true", help="Deploy to GitHub + GitHub Actions")
    parser.add_argument("--render", action="store_true", help="Deploy to Render.com")
    parser.add_argument("--fly", action="store_true", help="Deploy to Fly.io")
    parser.add_argument("--status", action="store_true", help="Show deployment status")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--client-id", help="Google OAuth Client ID")
    parser.add_argument("--client-secret", help="Google OAuth Client Secret")
    parser.add_argument("--next-steps", action="store_true", help="Print next steps only")

    args = parser.parse_args()

    if args.next_steps:
        print_next_steps()
        return

    if args.status:
        show_status()
        return

    # Handle GitHub deployment
    if args.github:
        token = args.github_token or os.getenv("GH_TOKEN")
        if not token:
            print("ERROR: Need GitHub token. Use --github-token or set GH_TOKEN env var.")
            print_next_steps()
            sys.exit(1)

        # Verify token works
        headers = {"Authorization": f"token {token}"}
        resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        if resp.status_code != 200:
            print("✗ Invalid GitHub token")
            sys.exit(1)

        print(f"✓ GitHub auth OK as: {resp.json().get('login', 'user')}")

        # Create repo if needed
        create_github_repo(token)

        # Upload files
        if upload_files_via_git(token):
            print("\n✓ GitHub deployment complete!")
            print(f"  Repository: {GITHUB_URL}")
            print_next_steps()

        return

    # Default: show status and next steps
    show_status()
    print_next_steps()


if __name__ == "__main__":
    main()
