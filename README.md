# Jinji2 - Custom Currency Tracker

A lightweight, dependency-minimal web application designed to track currency rates, manage user subscriptions, and visualize historical data.

The goal of this project was to understand the underlying mechanics of web servers by implementing routing and templating from scratch

## Key Features
- **Custom Web Server**: Built using native Python `http.server` (no heavy frameworks).
- **Relational DB**: SQLite integration with a focus on pure SQL queries for CRUD operations.
- **Subscription Logic**: Users can subscribe/unsubscribe from specific currencies.
- **Data Visualization**: Integrated Chart.js to render price dynamics from historical data.

## Tech Stack
- **Backend**: Python 3.11, Jinja2 (Templating).
- **Database**: SQLite3.
- **Frontend**: HTML/CSS, Chart.js.
