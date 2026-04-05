# Canteen Bot — InnoFood

A Telegram-based canteen ordering system for Innopolis University students.

**Bot:** [@InnoFood_bot](https://t.me/InnoFood_bot) — send /start to browse today's menu and place an order.

**Admin panel:** http://10.93.25.190:8080

## Problem

Students at Innopolis University cannot check the menu or order in advance — causing queues and uncertainty.

## Solution

A Telegram bot lets students browse and order instantly. Staff manage the menu and orders via the Canteen Admin web panel.

## Features

- **Telegram bot** — browse menu by category, add to cart, confirm order
- **Ready notification** — bot notifies student when order is ready for pickup
- **Cancel with reason** — staff picks a reason, student gets notified instantly
- **Canteen Admin panel** — 3 tabs: Menu / Orders / History
- **Menu tab** — add and remove daily menu items by category
- **Orders tab** — view active orders, mark ready or served, cancel with reason
- **History tab** — all served and cancelled orders archived here
- **Order state machine** — strict flow: pending → ready → served (invalid transitions blocked)
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
| API | http://10.93.25.190:8000 |
| Swagger docs | http://10.93.25.190:8000/docs |
| Admin panel | http://10.93.25.190:8080 |

## Order Flow

    Student  ->  /start -> browse menu -> add to cart -> confirm order
    Staff    ->  Orders tab: mark ready  -> student notified via Telegram
    Staff    ->  Orders tab: mark served -> moves to History tab
    Staff    ->  Orders tab: cancel (pick reason) -> student notified via Telegram

## Author

Timur Rasulov — SE Toolkit Hackathon 2026