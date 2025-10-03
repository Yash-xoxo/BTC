# ⛏ Bitcoin Lottery Miner Dashboard

A **multi-rig monitoring stack** for Bitcoin solo mining with cpuminer-opt. This project runs multiple CPU miners and a live dashboard to track hashrate, shares, uptime, and lottery odds.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Why Docker?](#-why-docker)
- [Why Python?](#-why-python)
- [Architecture](#architecture)
- [Project Structure](#-project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Overview

Bitcoin Lottery Miner Dashboard is a containerized monitoring solution for solo Bitcoin mining. It orchestrates multiple cpuminer-opt instances and provides a real-time web dashboard to track mining performance, statistics, and theoretical lottery odds of finding a block.

**⚠️ Important:** Solo mining Bitcoin with CPU has **extremely low probability** of success. This project is primarily for **educational purposes** and learning about mining infrastructure.

---

## Features

✅ **Multi-Rig Support** – Monitor multiple miners from a single dashboard  
✅ **Real-Time Stats** – Live hashrate, shares submitted, uptime tracking  
✅ **Lottery Odds Calculator** – Displays theoretical probability of finding a block  
✅ **Dockerized** – Complete isolation, portability, and reproducibility  
✅ **Easy Scaling** – Add more miners by editing `docker-compose.yml`  
✅ **REST API** – JSON endpoint for programmatic access to miner stats  
✅ **Lightweight** – Built on Flask + Gunicorn, minimal resource overhead  

---

## 🐳 Why Docker?

- **Isolation** – Miners and dashboard run in separate containers, no pollution of your host system
- **Portability** – Same configuration works on Linux, macOS, and Windows (with Docker Desktop)
- **Easy Scaling** – Add more miners without managing dependencies manually
- **Reproducibility** – Pinned versions ensure consistent behavior across environments
- **Simple Deployment** – One command to start the entire stack

---

## 🐍 Why Python?

The dashboard backend is written in **Python (Flask)** because:

- **Flask** is lightweight and perfect for serving APIs + simple HTML dashboards
- Python's built-in libraries (`socket`, `json`, `time`) make polling miner stats trivial
- **Easy to extend** – Add alerts, database logging, or advanced visualizations later
- **Wide compatibility** – Works on any platform with Python 3.11+

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           User Browser (Port 5000)          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│       Flask Dashboard (Gunicorn)            │
│  - Polls miner APIs every 5 seconds         │
│  - Calculates hashrate & lottery odds       │
│  - Serves web UI + REST API                 │
└──────────┬──────────────────────┬───────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│  Miner 1 (4048)  │   │  Miner 2 (4049)  │
│  cpuminer-opt    │   │  cpuminer-opt    │
│  → solo.ckpool   │   │  → solo.ckpool   │
└──────────────────┘   └──────────────────┘
```

**How It Works:**

1. **cpuminer-opt** instances run in separate Docker containers, mining against `solo.ckpool.org`
2. Each miner exposes a JSON API via TCP socket (ports 4048, 4049)
3. **Flask app** polls these sockets every 5 seconds, requesting `summary` stats
4. **Dashboard** parses JSON (hashrate, shares, uptime) and displays live metrics
5. **Gunicorn** serves Flask efficiently in production mode

---

## 📂 Project Structure

```
BTC/
├─ docker-compose.yml      # Orchestrates miners + dashboard
└─ dashboard/
    ├─ app.py              # Flask backend, polls miners via socket
    ├─ requirements.txt    # Python dependencies (Flask, gunicorn)
    ├─ Dockerfile          # Build instructions for dashboard image
    └─ templates/
        └─ index.html      # Frontend UI (HTML/CSS/JS)
```

---

### Installation Guides:

- [Docker for Linux](https://docs.docker.com/engine/install/)
- [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

Verify installation:

```bash
docker --version
docker compose version
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Yash-xoxo/BTC.git
cd BTC
```

Or manually create the project structure as shown in [Project Structure](#-project-structure).

### 2. Configure Your Bitcoin Wallet

Edit `docker-compose.yml` and replace the placeholder address:

```yaml
command: >
  cpuminer
  -a sha256d
  -o stratum+tcp://solo.ckpool.org:3333
  -u bc1YourRealBTCWalletAddress.LotteryMiner1  # ← CHANGE THIS
  --api-bind 0.0.0.0:4048
  -t 2
```

**⚠️ Critical:** Use a **real Bitcoin wallet address** or the pool will reject your shares.

### 3. Build and Start Containers

```bash
docker compose up -d --build
```

This will:
- Build the dashboard Docker image
- Pull the cpuminer-opt image
- Start 2 miner containers + 1 dashboard container

### 4. Verify Containers Are Running

```bash
docker compose ps
```

Expected output:

```
NAME                IMAGE                    STATUS
btc-miner1-1        minerstat/cpuminer-opt   Up 30 seconds
btc-miner2-1        minerstat/cpuminer-opt   Up 30 seconds
btc-dashboard-1     btc-dashboard            Up 30 seconds
```

---

## Configuration

### Adding More Miners

To add a third miner, edit `docker-compose.yml`:

```yaml
services:
  miner3:
    image: minerstat/cpuminer-opt:latest
    container_name: miner3
    command: >
      cpuminer
      -a sha256d
      -o stratum+tcp://solo.ckpool.org:3333
      -u bc1YourRealBTCWalletAddress.LotteryMiner3
      --api-bind 0.0.0.0:4050
      -t 2
    ports:
      - "4050:4050"
    restart: unless-stopped
```

Update `dashboard/app.py` to include the new miner:

```python
MINERS = [
    {"name": "Miner 1", "host": "miner1", "port": 4048},
    {"name": "Miner 2", "host": "miner2", "port": 4049},
    {"name": "Miner 3", "host": "miner3", "port": 4050},  # Add this
]
```

Rebuild and restart:

```bash
docker compose down
docker compose up -d --build
```

### Adjusting CPU Threads

Change the `-t` parameter in `docker-compose.yml`:

```yaml
command: >
  cpuminer
  ...
  -t 4  # Use 4 CPU threads instead of 2
```

---

## Usage

### Accessing the Dashboard

Open your browser and navigate to:

```
http://localhost:5000
```

You'll see:
- **Hashrate** for each miner
- **Shares Submitted** (accepted/rejected)
- **Uptime**
- **Lottery Odds** (probability of finding a block)

### REST API Endpoint

Get miner stats as JSON:

```bash
curl http://localhost:5000/api/miners
```

Example response:

```json
{
  "miners": [
    {
      "name": "Miner 1",
      "status": "online",
      "hashrate": 1250000,
      "shares": {"accepted": 42, "rejected": 0},
      "uptime": 3600
    },
    {
      "name": "Miner 2",
      "status": "online",
      "hashrate": 1180000,
      "shares": {"accepted": 39, "rejected": 1},
      "uptime": 3600
    }
  ],
  "total_hashrate": 2430000,
  "network_difficulty": 85000000000000,
  "lottery_odds": "1 in 35000000000"
}
```

---

## Monitoring

### View Logs

**Dashboard logs:**

```bash
docker logs -f btc-dashboard-1
```

**Miner logs:**

```bash
docker logs -f btc-miner1-1
docker logs -f btc-miner2-1
```

### Test Miner API Directly

Use `netcat` to query a miner:

```bash
echo '{"command":"summary"}' | nc localhost 4048
```

Expected response (JSON):

```json
{"hashrate":1250000,"shares":{"accepted":42,"rejected":0},"uptime":3600}
```

### Restart a Specific Service

```bash
docker compose restart miner1
docker compose restart dashboard
```

---

## Troubleshooting

### Problem: Dashboard shows "Miner Offline"

**Solution:**

1. Check if miners are running:
   ```bash
   docker compose ps
   ```

2. Verify miner API is accessible:
   ```bash
   echo '{"command":"summary"}' | nc localhost 4048
   ```

3. Check miner logs for errors:
   ```bash
   docker logs btc-miner1-1
   ```

### Problem: Miners rejected by pool

**Error in logs:** `Pool rejected share`

**Solution:** Ensure your Bitcoin wallet address is valid (starts with `bc1`, `1`, or `3`).

### Problem: High CPU usage

**Solution:** Reduce threads in `docker-compose.yml`:

```yaml
-t 1  # Use only 1 CPU thread
```

### Problem: Dashboard not loading

1. Check if port 5000 is already in use:
   ```bash
   lsof -i :5000
   ```

2. Change dashboard port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8080:8080"  # Use port 8080 instead
   ```

---


**Happy Mining! ⛏️**