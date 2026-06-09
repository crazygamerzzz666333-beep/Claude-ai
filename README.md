# ServerForge AI

ServerForge AI is a modular Discord bot built with Python 3.13, Disnake, PostgreSQL, Redis, FastAPI, and Docker. It automates Discord server creation, backups, templates, moderation, tickets, welcome flows, verification, analytics, and premium feature control.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

## Architecture

- `serverforge/bot`: Disnake bot, cogs, slash commands, and prefix commands.
- `serverforge/api`: FastAPI health, metrics, template, and backup API.
- `serverforge/core`: configuration, logging, localization, dependency container, scheduler.
- `serverforge/db`: async PostgreSQL access and schema migrations.
- `serverforge/services`: integrated domain services for AI plans, server building, templates, backups, moderation, tickets, logging, welcome, verification, analytics, premium, and security.

## Commands

Every command is exposed as both a slash command and a prefix command through paired cogs. Commands include permission checks, cooldowns, logging, localized help text, and centralized error handling.

## Development

```bash
python -m compileall serverforge tests
pytest
ruff check .
```
