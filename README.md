# FlightPulseProject

End-to-end project for flight status / delay intelligence with:

- **Frontend** — UI for searching/visualizing
- **Backend** — API + integrations
- **AI** — notebooks, trained model, and data (tracked with **Git LFS**)

> **Large files**  
> This repo uses **Git LFS** for big artifacts (e.g., `.csv`, `.zip`, `.pkl`, `.xlsx`).  

---

## Table of Contents

- [Overview](#overview)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [AI / Model](#ai--model)
- [Deployment (AWS SAM • AWS Lambda)](#deployment-aws-sam--aws-lambda)
  - [Prerequisites](#prerequisites-1)
  - [One-time guided deploy](#one-time-guided-deploy)
  - [Subsequent deploys](#subsequent-deploys)
  - [Local testing (without deploying)](#local-testing-without-deploying)
  - [Environment variables / secrets](#environment-variables--secrets)
  - [Logs & troubleshooting](#logs--troubleshooting)
  - [Clean up (delete stack and resources)](#clean-up-delete-stack-and-resources)
- [Configuration](#configuration)
- [Data & Reproducibility](#data--reproducibility)
- [Common Scripts](#common-scripts)


---

## Overview

**FlightPulseProject** combines a web UI, a Python backend API, and an AI workspace for flight delay/cancellation prediction.  
The AI workspace includes a notebook (`FlightDelayPredictor.ipynb`), a trained model (`flight_cancellation_model.pkl`), and
monthly 2019 CSV datasets used for experimentation. The backend is serverless: deployed to **AWS Lambda** behind **API Gateway** using **AWS SAM**.


---

## Repository Layout

```text
FlightPulseProject/
├─ flightpulse-frontend/            # Web app (Node/JS/TS stack)
├─ flightpulse-backend/             # Python backend API and utilities
├─ FlightAI/                        # AI workspace (notebooks, model, data)
│  ├─ FlightDelayPredictor.ipynb
│  ├─ flight_cancellation_model.pkl
│  ├─ 05-2019.csv ... 12-2019.csv   # large CSVs (via Git LFS)
│  ├─ predict.py                    # sample inference script (if provided)
│  └─ model_features.pkl            # features metadata (if provided)
├─ .gitattributes                   # LFS rules for *.csv, *.zip, *.pkl, *.xlsx, etc.
├─ .gitignore                       # ignores logs, caches, envs, build outputs
└─ README.md
```
---

## Prerequisites

- **Git** and **Git LFS** installed  
- **Node.js** ≥ 18 (for the frontend)  
- **Python** ≥ 3.10 (for the backend and AI workspace)  
- Optional: **virtualenv**, **pipenv**, or **poetry** for Python environments

---

## Quickstart

Clone with LFS and enter the repo:

```bash
git clone https://github.com/AdeshKessani/FlightPulseProject.git
cd FlightPulseProject
git lfs pull
```

---

### Backend

```bash
cd flightpulse-backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Start the server (adjust entrypoint if different)
python main.py

# or, for ASGI apps:
# uvicorn app:app --reload --port 8000
```

---

### Frontend

```bash
cd flightpulse-frontend
npm install

# Dev server
npm run dev

# Production build + preview
npm run build && npm run preview
```

---

## Deployment (AWS SAM • AWS Lambda)

This backend can be deployed serverlessly using **AWS SAM** (Serverless Application Model) to **AWS Lambda** behind **Amazon API Gateway**.

### Prerequisites
- AWS account + credentials configured locally (`aws configure`)
- **AWS CLI** and **AWS SAM CLI** installed
- (Optional) `docker` for local emulation via `sam local`

### One-time guided deploy
```bash
cd flightpulse-backend
sam build
sam deploy --guided
```
During `--guided`, you will be prompted for:

- **Stack Name** (e.g., `flightpulse-backend`)
- **AWS Region** (e.g., `us-east-1`)
- **Allow SAM to create roles** → `Y`
- **Save arguments to samconfig.toml** → `Y` (so future deploys are one command)

When it finishes, SAM prints your **API Gateway endpoint**. Use that as the backend base URL.

### Subsequent deploys
```bash
cd flightpulse-backend
sam build && sam deploy
```
### Local testing (without deploying)

Run the API locally with Lambda emulation:
```bash
cd flightpulse-backend
sam build
sam local start-api
# then call http://127.0.0.1:3000/<your-route>
```
Invoke a single function with an event:
```bash
sam local invoke <FunctionName> -e events/event.json
```
### Environment variables / secrets

- Configure per-function env vars in `template.yaml` (SAM template) or via `sam deploy --parameter-overrides`.
- For sensitive values, prefer **AWS Systems Manager Parameter Store** or **AWS Secrets Manager**; fetch at runtime instead of committing to Git.

### Logs & troubleshooting
```bash
# Tail CloudWatch logs for a function
sam logs -n <FunctionName> --stack-name <StackName> --tail
```
### Clean up (delete stack and resources)
```bash
sam delete --stack-name <StackName>
```
> **Note:** If your frontend needs the deployed API, set  
> `VITE_API_BASE=https://<api-id>.execute-api.<region>.amazonaws.com/<stage>`  
> in `flightpulse-frontend/.env`.


---


### AI / Model

```bash
cd FlightAI
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# If a requirements file exists:
pip install -r requirements.txt

# Work with the notebook:
# jupyter lab    OR    jupyter notebook

# CLI help (if provided):
python predict.py --help
```

---

## Configuration


**`flightpulse-backend/.env`**
```dotenv
API_KEY=your_real_api_key_here
MODEL_PATH=./FlightAI/flight_cancellation_model.pkl
PORT=8000
```
**`flightpulse-frontend/.env` (Vite style)**
```dotenv
VITE_API_BASE=http://localhost:8000
```

---

## Data & Reproducibility

- Large datasets and model artifacts are tracked via **Git LFS**.
- If LFS quotas are a concern, include a **small sample** in the repo for quick tests and document where full data can be fetched.
- Document columns, source, license, and preprocessing in this README or `DATA.md`.

---

## Common Scripts


### Frontend
```bash
npm run dev      # start dev server
npm run build    # production build
npm run preview  # preview built app
```
### Backend
```bash
python main.py                 # start API
# or:
uvicorn app:app --reload
```
### AI
```bash
jupyter lab                    # open notebooks
python predict.py              # example inference CLI


