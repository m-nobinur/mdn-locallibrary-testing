# Phase 1 Evidence — Clean Start and Baseline Setup

This folder contains the evidence artefacts for Phase 1 of the project, covering the clean start, environment setup, and baseline verification of the MDN LocalLibrary application.

## What this phase proves

- the application runs locally after dependency installation and migrations
- the Django admin is reachable after superuser creation
- the public GitHub repository and remotes setup were completed

## Verification summary

- created the local environment with `uv venv .venv`
- installed runtime dependencies from `requirements.txt`
- applied Django migrations successfully
- created a superuser account
- verified the public catalogue page, admin dashboard, and GitHub repository state

## Evidence files

### Home page

Confirms the LocalLibrary application is running and the public-facing catalogue page loads successfully.

![Phase 1 home page evidence](./home-page.png)

### Admin dashboard

Confirms that Django admin access is working after the baseline setup and superuser creation steps.

![Phase 1 admin dashboard evidence](./admin-dashboard.png)

### GitHub repository

Confirms the public repository exists and the project setup evidence is visible on GitHub.

![Phase 1 GitHub repository evidence](./github-repo.png)