# InnoFood — Canteen Bot

A Telegram-based canteen ordering system for Innopolis University students.

**Bot:** [@InnoFood_bot](https://t.me/InnoFood_bot) — send `/start` to browse today's menu and place an order.

## Problem

Students at Innopolis University cannot check the menu or order in advance — causing queues and uncertainty.

## Solution

A Telegram bot lets students browse and order instantly. Staff manage the menu and orders via a web admin panel.

## Features

- **Telegram bot** — browse menu by category, add to cart, confirm order
- **Ready notification** — bot notifies student when order is ready for pickup
- **Cancel with reason** — staff picks a reason, student gets notified instantly
- **Web admin panel** — add/remove menu items, manage active orders, view history
- **Order state machine** — strict flow: pending → ready → served (invalid transitions blocked)
- **Order history tab** — served and cancelled orders archived separately
- **Auto-refresh** — Orders tab polls every 5 seconds automatically
- **REST API** — full CRUD with Swagger docs at /docs
- **Dockerized** — all 4 services start with a single command

## Stack

| Component | Tech |
|-----------|------|
| Bot | python-telegram-bot 21 + aiohttp |
| Backend | FastAPI + asyncpg + databases |
| Database | PostgreSQL 16 |
| Admin UI | nginx + HTML/JS |
| Deploy | Docker Compose on Ubuntu 24.04 |

## Quick Start

Requirements: Docker + Docker Compose + Telegram bot token from @BotFather

    git clone https://github.com/Timur-Inno/se-toolkit-hackathon.git
    cd se-toolkit-hackathon
    cp .env.example .env
    nano .env  # set TELEGRAM_BOT_TOKEN
    docker compose up -d

| Service | URL |
|---------|-----|
| API | http://SERVER_IP:8000 |
| Swagger docs | http://SERVER_IP:8000/docs |
| Admin panel | http://SERVER_IP:8080 |

## Order Flow

    Student  ->  /start -> browse -> add to cart -> confirm
    Staff    ->  mark ready  -> student notified
    Staff    ->  mark served -> moves to History
    Staff    ->  cancel (pick reason) -> student notified

## Author

Timur Rasulov — SE Toolkit Hackathon 2026