# Git Quick Reference - Matrimony HR AI

## 🚀 Quick Start

```bash
# Initialize and first commit
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub
git remote add origin https://github.com/yourusername/matrimony-hr-ai.git
git push -u origin main
```

## 📝 Daily Workflow

```bash
# 1. Check what changed
git status

# 2. Add your changes
git add .

# 3. Commit with message
git commit -m "Your message here"

# 4. Push to remote
git push
```

## 🔍 What's Ignored?

✅ **Safe to commit:**
- Source code (`.py`, `.js`, `.jsx`, `.css`)
- Config files (`package.json`, `requirements.txt`)
- Documentation (`.md` files)
- `.env.example` (template)

❌ **Automatically ignored:**
- `node_modules/` (500+ MB)
- `venv/` (100+ MB)
- `*.db` (databases)
- `.env` (secrets!)
- `server/data/uploads/*` (user files)
- `__pycache__/`, `.pytest_cache/`

## 🌿 Branching

```bash
# Create and switch to new branch
git checkout -b feature/my-feature

# Switch back to main
git checkout main

# Merge feature into main
git merge feature/my-feature

# Delete branch
git branch -d feature/my-feature
```

## 🔄 Syncing

```bash
# Get latest changes
git pull

# Push your changes
git push

# Force pull (discard local changes)
git fetch origin
git reset --hard origin/main
```

## ⚠️ Common Issues

### Forgot to pull before commit?
```bash
git pull --rebase
git push
```

### Accidentally committed .env?
```bash
git rm --cached .env
git commit -m "Remove .env"
git push
```

### Want to undo last commit?
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### See what's ignored?
```bash
git status --ignored
```

## 📊 Repository Info

```bash
# View commit history
git log --oneline

# See file changes
git diff

# Check repo size
git count-objects -vH

# List all branches
git branch -a
```

## 🔐 Security Checklist

Before committing:
- [ ] `.env` is in `.gitignore`
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No database files
- [ ] No large binary files

## 🎯 Commit Message Format

```bash
# Good examples:
git commit -m "Feature: Add multilingual interview support"
git commit -m "Fix: Resolve sidebar animation bug"
git commit -m "Docs: Update README with setup instructions"
git commit -m "Refactor: Improve question generation logic"
git commit -m "Style: Format code with prettier"

# Types: Feature, Fix, Docs, Refactor, Style, Test, Chore
```

## 🤝 Team Collaboration

```bash
# Clone repository
git clone https://github.com/yourusername/matrimony-hr-ai.git

# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Feature: Add new functionality"

# Push feature branch
git push -u origin feature/my-feature

# Create Pull Request on GitHub
# After merge, update local main
git checkout main
git pull
```

## 📦 After Cloning

```bash
# 1. Install Node dependencies
cd client
npm install

# 2. Install Python dependencies
cd ../server
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Set up environment
cd ..
copy .env.example .env  # Edit with your keys
```

## 🆘 Emergency Commands

```bash
# Discard ALL local changes
git reset --hard HEAD
git clean -fd

# Restore specific file
git checkout -- filename.py

# Stash changes temporarily
git stash
git stash pop

# View stashed changes
git stash list
```

## 📱 GitHub Desktop (GUI Alternative)

If you prefer a visual interface:
1. Download: https://desktop.github.com/
2. Clone your repository
3. Make changes
4. Commit with description
5. Push to origin

---

**Pro Tip:** Run `git status` frequently to see what's happening!

**Remember:** The `.gitignore` is already configured - just use `git add .` safely! 🎉
