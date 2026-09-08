# Smart Greenhouse

A full-stack Smart Greenhouse application built with FastAPI, PostgreSQL, React, TypeScript, and Tailwind CSS.

## Stack

* Backend: FastAPI + SQLAlchemy + Alembic
* Database: PostgreSQL 16
* API reference: Scalar
* Frontend: Vite + React + TypeScript + Tailwind CSS v4

## Prerequisites

Before starting the project, install:

* Python 3.11 or newer
* Docker Desktop
* Node.js and npm

## First-time setup

### 1. Start PostgreSQL

Open a terminal in the project root:

docker compose up -d


Check that PostgreSQL is healthy:

docker compose ps


The `greenhouse-postgres` container should show as healthy.

### 2. Set up the backend

From the project root:

cd backend

Create and activate the Python virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install the project dependencies:

pip install -e ".[dev]"


Apply the database migration:

alembic upgrade head


### 3. Set up the frontend

From the project root:

cd frontend
npm install

## Daily start

Use three terminals.

### Terminal 1 — PostgreSQL

From the project root:

docker compose up -d

### Terminal 2 — Backend

From the project root:

cd backend
.\.venv\Scripts\Activate.ps1
cd src
uvicorn main:app --reload --port 8000

### Terminal 3 — Frontend

From the project root:

cd frontend
npm run dev

## URLs

* API: http://localhost:8000
* Health check: http://localhost:8000/health
* Scalar API reference: http://localhost:8000/scalar
* OpenAPI schema: http://localhost:8000/openapi.json
* Frontend: http://localhost:5173
* Dashboard: http://localhost:5173/dashboard

The standard FastAPI `/docs` endpoint is disabled in this project.

## Phase 1

Phase 1 provides the initial project skeleton, PostgreSQL database connection, health endpoint, Scalar API reference, frontend routing, Tailwind CSS styling, health status display, and six dashboard placeholder sections.

## Documentation

See:

`docs/phases/README.md`