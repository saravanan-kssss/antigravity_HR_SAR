# Git Setup Guide for Matrimony HR AI

This guide will help you set up Git version control for your project.

## Initial Setup

### 1. Initialize Git Repository (if not already done)

```bash
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: Matrimony HR AI with multilingual support"
```

## What's Ignored by .gitignore

The `.gitignore` file automatically excludes:

### 📦 Dependencies (Can be reinstalled)
- `node_modules/` - Node.js packages
- `venv/`, `env/` - Python virtual environments

### 🗄️ Databases & Uploads
- `*.db` - SQLite databases
- `server/data/uploads/*` - Uploaded resumes
- `server/data/media/*` - Interview recordings
- `server/data/frames/*` - Proctoring frames

### 🔐 Secrets & Environment
- `.env` - Environment variables with API keys
- `*.json` - Google Cloud credentials (except config files)

### 🏗️ Build Artifacts
- `dist/`, `build/` - Production builds
- `__pycache__/` - Python bytecode
- `.pytest_cache/` - Test cache

### 💻 IDE Settings
- `.vscode/` - VS Code settings
- `.kiro/` - Kiro IDE settings
- `.idea/` - JetBrains IDEs

### 📝 Temporary Files
- `*.log` - Log files
- `*.tmp`, `*.temp` - Temporary files
- `*.zip` - Zip archives

## What's Included in Git

✅ All source code (`.py`, `.js`, `.jsx`, `.css`)
✅ Configuration files (`package.json`, `requirements.txt`)
✅ Documentation (`.md` files)
✅ `.env.example` (template for environment variables)
✅ Directory structure (via `.gitkeep` files)

## Common Git Commands

### Check Status
```bash
git status
```

### Add Changes
```bash
# Add all changes
git add .

# Add specific file
git add server/main.py

# Add specific folder
git add client/src/
```

### Commit Changes
```bash
git commit -m "Add feature: multilingual interview support"
```

### View History
```bash
git log --oneline
```

### Create Branch
```bash
git branch feature/new-feature
git checkout feature/new-feature

# Or in one command
git checkout -b feature/new-feature
```

### Push to Remote (GitHub/GitLab)
```bash
# First time setup
git remote add origin https://github.com/yourusername/matrimony-hr-ai.git
git branch -M main
git push -u origin main

# Subsequent pushes
git push
```

## Setting Up Remote Repository

### GitHub

1. Create a new repository on GitHub
2. Don't initialize with README (you already have one)
3. Copy the repository URL
4. Run:

```bash
git remote add origin https://github.com/yourusername/matrimony-hr-ai.git
git branch -M main
git push -u origin main
```

### GitLab

```bash
git remote add origin https://gitlab.com/yourusername/matrimony-hr-ai.git
git branch -M main
git push -u origin main
```

## Cloning the Repository (For Team Members)

```bash
# Clone the repository
git clone https://github.com/yourusername/matrimony-hr-ai.git
cd matrimony-hr-ai

# Install Node.js dependencies
cd client
npm install
cd ..

# Install Python dependencies
cd server
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cd ..

# Set up environment variables
copy .env.example .env  # Windows
# or: cp .env.example .env  # Linux/Mac
# Then edit .env with your API keys
```

## Best Practices

### 1. Commit Often
Make small, focused commits with clear messages:
```bash
git commit -m "Fix: Resolve sidebar animation issue"
git commit -m "Feature: Add Hindi language support"
git commit -m "Docs: Update README with setup instructions"
```

### 2. Use Meaningful Branch Names
```bash
git checkout -b feature/ats-scoring
git checkout -b fix/login-redirect
git checkout -b docs/api-documentation
```

### 3. Pull Before Push
```bash
git pull origin main
git push origin main
```

### 4. Review Changes Before Committing
```bash
git diff
git status
```

### 5. Never Commit Secrets
- Always use `.env` files for secrets
- Keep `.env` in `.gitignore`
- Use `.env.example` as a template

## Troubleshooting

### Accidentally Committed .env File

```bash
# Remove from Git but keep locally
git rm --cached .env
git commit -m "Remove .env from version control"
git push
```

### Undo Last Commit (Keep Changes)

```bash
git reset --soft HEAD~1
```

### Discard All Local Changes

```bash
git reset --hard HEAD
```

### View What's Ignored

```bash
git status --ignored
```

## GitHub Actions / CI/CD (Optional)

Create `.github/workflows/test.yml` for automated testing:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd server
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd server
          pytest
```

## Repository Size Management

Your repository should be:
- **Without ignored files:** ~5-20 MB
- **With ignored files:** 500+ MB (don't commit these!)

If your repo is too large, check:
```bash
git count-objects -vH
```

## Need Help?

- Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf

---

**Remember:** The `.gitignore` file is already configured to protect your secrets and exclude unnecessary files. Just use `git add .` safely!
