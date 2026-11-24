"""
Auto YouTube Pipeline — Deployment Setup Script
Usage: python deploy/setup.py [GITHUB_TOKEN]
       or: GH_TOKEN=your_token python deploy/setup.py
"""
import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from github import Github
except ImportError:
    print("ERROR: Install PyGithub first: pip install PyGithub")
    sys.exit(1)


def run_cmd(cmd):
    """Run shell command and return success."""
    return os.system(cmd) == 0


class Deployer:
    def __init__(self, token):
        self.token = token
        self.gh = Github(token)
        self.user = self.gh.get_user()
        self.repo_name = "auto-youtube-pipeline"
        # Will be set dynamically in create_or_get_repo based on authenticated user
        self.project_root = Path(__file__).parent.parent.resolve()

    def create_or_get_repo(self):
        """Create GitHub repo if it doesn't exist."""
        from github import Auth

        auth = Auth.Token(self.token)
        gh = Github(auth=auth)
        self.user = gh.get_user()
        self.gh = gh

        # Use authenticated user's actual username, not hardcoded one
        self.repo_owner = self.user.login

        try:
            repo = gh.get_repo(f"{self.repo_owner}/{self.repo_name}")
            print("[OK] Repository exists: https://github.com/{self.repo_owner}/{self.repo_name}")
            return repo
        except Exception:
            pass

        print(f"\nCreating repository: {self.repo_name}...")
        # Create via REST API instead
        import requests
        resp = requests.post(
            "https://api.github.com/user/repos",
            json={
                "name": self.repo_name,
                "description": "Auto AI Video Generation & YouTube Upload Pipeline",
                "private": False
            },
            headers={"Authorization": f"token {self.token}"},
            timeout=30
        )
        if resp.status_code == 201:
            repo = gh.get_repo(f"{self.repo_owner}/{self.repo_name}")
            print("[OK] Repository created: https://github.com/{repo.full_name}")
            return repo
        elif resp.status_code == 422:
            # Repo might already exist but we couldn't access it
            print("[!] Repository may already exist")
            return None
        else:
            raise Exception(f"Failed to create repo: {resp.status_code} {resp.text[:200]}")

    def push_to_github(self):
        """Push all code files to GitHub using git."""
        os.chdir(self.project_root)

        # Remove any existing remote
        run_cmd('git remote remove origin 2>/dev/null')

        # Set remote with token auth
        remote_url = f"https://{self.token}@github.com/{self.repo_owner}/{self.repo_name}.git"
        run_cmd(f'git remote add origin "{remote_url}"')

        # Stage and commit
        run_cmd('git add .')
        run_cmd('git commit -m "Auto YouTube Pipeline v1.0 - Ready for deployment" --allow-empty')
        run_cmd('git branch -M main')

        # Push
        result = run_cmd('git push -u origin main --force')

        if result:
            print("[OK] Files pushed to GitHub successfully")
            return True
        else:
            print("✗ Failed to push to GitHub")
            return False

    def setup_workflow(self):
        """Create GitHub Actions workflow file."""
        repo = self.gh.get_repo(f"{self.repo_owner}/{self.repo_name}")

        workflow_content = """name: Daily YouTube Pipeline

on:
  schedule:
    # Runs daily at 6:00 AM UTC (2am EST / 7am IST)
    - cron: '0 6 * * *'
  workflow_dispatch:  # Allow manual trigger

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

      - run: sudo cp -r assets/dejavu-fonts-ttf-2.37/ttf/*.ttf /usr/share/fonts/truetype/dejavu/
             sudo fc-cache -fv

      - run: ffmpeg -version | head -1

      - name: Run pipeline test
        env:
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
        run: |
          source venv/bin/activate
          cd scripts
          python test_pipeline.py

      - run: find output/ -name "*.mp4" -type f

      - run: echo "Daily pipeline execution completed successfully"
"""
        # Ensure directory structure
        try:
            repo.get_contents(".github/workflows/daily.yml")
        except:
            pass

        try:
            contents = repo.get_contents(".github/workflows/daily.yml")
            sha = contents.sha
            repo.update_file(".github/workflows/daily.yml",
                           "Update daily workflow config",
                           base64.b64encode(workflow_content.encode()).decode(),
                           sha)
        except:
            repo.create_file(".github/workflows/daily.yml",
                           "Add daily workflow config",
                           base64.b64encode(workflow_content).decode())

        print("[OK] GitHub Actions workflow configured")

    def guide_youtube_setup(self):
        """Print YouTube API setup instructions."""
        print("\n" + "="*60)
        print(" YOUTUBE API SETUP (Required for Video Upload)")
        print("="*60)
        print("""
Step 1: Create Google Cloud Project
  1. Go to: https://console.cloud.google.com/
  2. Click "Select a project" -> "New Project"
  3. Name: "auto-youtube-pipeline" -> Create

Step 2: Enable YouTube Data API
  1. Left menu: APIs & Services -> Library
  2. Search "YouTube Data API v3" -> Enable

Step 3: Create OAuth Credentials
  1. Left menu: APIs & Services -> Credentials
  2. "+ CREATE CREDENTIALS" -> "OAuth client ID"
  3. Application type: "Desktop app"
  4. Name: "auto-youtube-uploader"
  5. Download JSON file

Step 4: Generate Refresh Token (for auto-upload)
  Method A - Browser (easiest):
    Run locally on your computer:
      cd D:\\PROJECT\\Coding\\auto-youtube-pipeline
      python scripts/setup_auth.py

  Method B - Manual URL:
    Visit this URL (replace CLIENT_ID):
    https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/youtube.upload&response_type=code&access_type=offline

    After authorization, copy the 'code' parameter from redirect URL

Step 5: Add Secrets to GitHub
  1. Go to: https://github.com/rajubai6419/auto-youtube-pipeline/settings/secrets/actions
  2. Click "New repository secret"
  3. Add these secrets:
     * YOUTUBE_REFRESH_TOKEN (from Step 4)
* GOOGLE_CLIENT_ID (from downloaded JSON)
* GOOGLE_CLIENT_SECRET (from downloaded JSON)
""")


def main():
    print("\n" + "="*60)
    print(" Auto YouTube Pipeline — Deployment Setup")
    print("="*60)

    # Get GitHub token from args or env
    token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GH_TOKEN", "")

    if not token:
        print("\nPlease provide your GitHub Personal Access Token:")
        print("  • Go to: https://github.com/settings/tokens/new")
        print("  • Scopes: repo, workflow")
        print("  • Or set: GH_TOKEN=your_token python deploy/setup.py")
        sys.exit(1)

    print(f"\nAuthenticating as: ", end="", flush=True)

    try:
        deployer = Deployer(token)
        print(deployer.user.login)
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        sys.exit(1)

    # Execute deployment steps
    deployer.create_or_get_repo()
    deployer.push_to_github()
    deployer.setup_workflow()
    deployer.guide_youtube_setup()

    print("\n" + "="*60)
    print(" DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"\nRepository: https://github.com/{deployer.repo_owner}/{deployer.repo_name}")
    print("\nNext steps:")
    print("  1. Add YouTube secrets to GitHub (see above guide)")
    print("  2. Videos will generate daily at 6:00 AM UTC automatically")
    print("  3. With YouTube credentials: videos upload to your channel")
    print("  4. Without credentials: videos save locally in output/")
    print("\nMonitor your pipeline:")
    print(f"  https://github.com/{deployer.repo_owner}/{deployer.repo_name}/actions\n")


if __name__ == "__main__":
    main()
