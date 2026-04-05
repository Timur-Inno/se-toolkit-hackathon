# InnoFood - Canteen Bot

A Telegram-based food ordering system for Innopolis University students.

**Bot:** [@InnoFood_bot](https://t.me/InnoFood_bot) - send /start to browse today's menu and place an order.

**Admin panel:** http://10.93.25.190:8080

## Problem

Students at Innopolis University have no way to check menus or order food in advance, causing queues and uncertainty about what is available.

## Solution

A Telegram bot lets students pick a food place, browse the menu, and order instantly. Staff at each venue manage their menu and orders through a shared web admin panel.

## Venues

- Happiness - main dishes, snacks, drinks, desserts
- Neuro Coffee - coffee, lattes, teas, pastries
- In Joy - coffee, lattes, teas, pastries
- Canteen - soups, mains, sides, drinks, desserts

## Features

- Venue selection at the start of every order
- Browse menu by category per venue
- Add items to cart and confirm order
- Notification when order is ready for pickup
- Cancel with reason - student gets notified instantly
- Admin panel with Menu, Orders, and History tabs
- Orders filtered per venue so each place sees only their orders
- Order state flow: pending -> ready -> served
- Auto-refresh on the Orders tab every 5 seconds
- REST API with Swagger docs at /docs
- PostgreSQL for persistent storage
- Fully dockerized, all services start with one command

## Stack

| Component | Tech |
|-----------|------|
| Bot | python-telegram-bot 21 + aiohttp |
| Backend | FastAPI + asyncpg + databases |
| Database | PostgreSQL 16 |
| Admin UI | nginx + HTML/JS |
| Deploy | Docker Compose on Ubuntu 24.04 |

## Quick Start

Requirements: Docker, Docker Compose, Telegram bot token from @BotFather

    git clone https://github.com/Timur-Inno/se-toolkit-hackathon.git
    cd se-toolkit-hackathon
    cp .env.example .env
    nano .env
    docker compose up -d

| Service | URL |
|---------|-----|
| API | http://SERVER_IP:8000 |
| Swagger docs | http://SERVER_IP:8000/docs |
| Admin panel | http://SERVER_IP:8080 |

## Order Flow

    Student  ->  /start -> pick venue -> browse menu -> add to cart -> confirm
    Staff    ->  Orders tab: mark ready  -> student notified via Telegram
    Staff    ->  Orders tab: mark served -> moves to History tab
    Staff    ->  Orders tab: cancel with reason -> student notified via Telegram

## Author

Timur Rasulov - SE Toolkit Hackathon 2026
