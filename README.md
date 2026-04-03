# Project Setup

## Set up Repo
In Github:
Create new repo called assignment_10 and make sure it is public

In WSL/VS Code Terminal:
```bash
mkdir assignment_10
cd assignment_10/
git init
git branch -m main
git remote add origin git@github.com:mbel12345/assignment_10.git
vim README.md
git add . -v
git commit -m "Initial commit"
git push -u origin main
```

## Set up virtual environment
In WSL/VS Code Terminal:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
