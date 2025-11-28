# Creating Project Zip File

This guide explains how to create a clean zip file of the Matrimony HR AI project, excluding unnecessary files like dependencies and cache.

## Quick Start (Windows)

### Option 1: Double-click the batch file
Simply double-click `create-zip.bat` in Windows Explorer.

### Option 2: Run PowerShell script
```powershell
.\create-zip.ps1
```

### Option 3: Using 7-Zip (if installed)
```cmd
7z a -tzip Matrimony_HR_AI.zip . -xr!node_modules -xr!venv -xr!__pycache__ -xr!.pytest_cache -xr!.hypothesis -xr!.git -xr!.vscode -xr!.kiro -xr!*.db -xr!.env
```

### Option 4: Using Git Bash or WSL
```bash
zip -r Matrimony_HR_AI.zip . \
    -x "*/node_modules/*" \
    -x "*/venv/*" \
    -x "*/__pycache__/*" \
    -x "*/.pytest_cache/*" \
    -x "*/.hypothesis/*" \
    -x "*/.git/*" \
    -x "*/.vscode/*" \
    -x "*/.kiro/*" \
    -x "*.db" \
    -x "*/.env" \
    -x "*/dist/*" \
    -x "*/build/*"
```

## What Gets Excluded

The following files and folders are automatically excluded:

### Folders:
- `node_modules/` - Node.js dependencies (can be reinstalled with `npm install`)
- `venv/` - Python virtual environment (can be recreated)
- `__pycache__/` - Python bytecode cache
- `.pytest_cache/` - Pytest cache
- `.hypothesis/` - Hypothesis testing cache
- `.git/` - Git repository data
- `.vscode/` - VS Code settings
- `.kiro/` - Kiro IDE settings
- `dist/` - Build output
- `build/` - Build artifacts

### Files:
- `*.db` - Database files (interview.db, interviews.db)
- `*.pyc` - Python compiled files
- `*.pyo` - Python optimized files
- `*.log` - Log files
- `.env` - Environment variables (contains secrets)

## What Gets Included

- All source code (`.py`, `.js`, `.jsx`, `.css`, etc.)
- Configuration files (`package.json`, `requirements.txt`, etc.)
- Documentation (`.md` files)
- `.env.example` (template for environment variables)
- Static assets and resources

## After Extracting the Zip

Recipients will need to:

1. **Install Node.js dependencies:**
   ```bash
   cd client
   npm install
   ```

2. **Install Python dependencies:**
   ```bash
   cd server
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in the required API keys and configuration

4. **Initialize database:**
   - The database will be created automatically on first run

## Troubleshooting

### PowerShell Execution Policy Error
If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 7-Zip Not Found
Download and install 7-Zip from: https://www.7-zip.org/

### Zip Command Not Found (Git Bash)
Install Git for Windows which includes Git Bash: https://git-scm.com/download/win

## File Size Expectations

- **With excluded files:** ~5-20 MB (source code only)
- **Without exclusions:** 500+ MB (includes node_modules, venv, etc.)

The exclusions reduce the zip file size by 95%+ while keeping all essential code!
