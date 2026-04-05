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

## Build image and start container
Note: This must be up-and-running for all local testing
In WSL/VS Code Terminal:
```bash
docker compose up --build
```

## Run app as stand-alone Python app
In WSL/VS Code Terminal:
```bash
python3 main.py
```

In Browser, go to:
http://localhost:8000/

## Run test cases locally
In WSL/VS Code Terminal:
```bash
pytest
```

## Configure Github Actions
Github Actions will run on any pushes or pull requests. Only pull requests will result in the deployment step.
Pre-requisite: In Dockerhub, create an Access Token, then add it to Environment var "DOCKERHUB_PASSWORD" in GitHub. Add DOCKERHUB_USERNAME also.

Add these environment variables in Github:
  - POSTGRES_USER = postgres
  - POSTGRES_PASSWORD = postgres

NOTE: Do all github actions work on main branch, to eliminate the manual steps of merging a PR to test any changes. In a real DEV environment at work, feature branches should still be used.
