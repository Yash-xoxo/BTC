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

`docker pull cniweb/cpuminer-opt:latest`

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
│    Flask Dashboard (Gunicorn on :8080)      │
│  - Polls miner APIs every few seconds       │
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

1. **Miners** (`cniweb/cpuminer-opt`) run SHA256d hashing against Bitcoin via `solo.ckpool.org`. Each miner exposes an API on TCP (ports 4048, 4049)
2. **Dashboard backend** (`dashboard/app.py`) is a Flask app that opens a socket to each miner, requests `summary`, parses JSON, and stores samples in memory
3. **Frontend** (`dashboard/templates/index.html`) is a styled HTML dashboard that polls `/api/miners` every few seconds and updates stats live
4. **Dockerfile** builds a minimal Python + Flask image with Gunicorn
5. **Docker Compose** spins up miners and dashboard together, wiring their networks automatically


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

Check they're running:

```bash
docker ps
```

You should see:
- `btc-miner1-1` (port 4048)
- `btc-miner2-1` (port 4049)
- `btc-dashboard-1` (port 5000 → 8080 inside)

### 5. Check Logs

**For miner logs:**

```bash
docker logs -f btc-miner1-1
```

Look for:

```
API listening to 0.0.0.0:4048
accepted: 1/1 (100.00%), ...
```

**For dashboard logs:**

```bash
docker logs -f btc-dashboard-1
```

Look for:

```
[INFO] Listening at: http://0.0.0.0:8080
```

---


## Configuration

## 📈 Scaling

To add more miners:

### 1. Add Miner to Docker Compose

Copy one of the `miner` blocks in `docker-compose.yml` and modify:

```yaml
  miner3:
    image: cniweb/cpuminer-opt:latest
    container_name: miner3
    command:
      - "cpuminer"
      - "-a"
      - "sha256d"
      - "-o"
      - "stratum+tcp://solo.ckpool.org:3333"
      - "-u"
      - "bc1YourRealBTCWallet.LotteryMiner3"  # Change worker name
      - "-p"
      - "x"
      - "-t"
      - "4"
      - "--api-bind=0.0.0.0:4050"  # New port
    ports:
      - "4050:4050"  # Map new port
    restart: unless-stopped
```

### 2. Update Dashboard Configuration

Add the new miner to the `MINERS` environment variable in the `dashboard` service:

```yaml
dashboard:
  build: ./dashboard
  ports:
    - "5000:8080"
  environment:
    - MINERS=miner1:4048,miner2:4049,miner3:4050  # Add miner3
  depends_on:
    - miner1
    - miner2
    - miner3  # Add dependency
```

### 3. Rebuild and Restart

```bash
docker compose down
docker compose up -d --build
```

The new miner will automatically appear on the dashboard!

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

### Start Everything

```bash
docker compose up -d --build
```

### Stop Everything

```bash
docker compose down
```

### Restart Just Dashboard

After making code changes:

```bash
docker compose build dashboard
docker compose up -d dashboard
```

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

### Debug Miner API Directly

Use `netcat` to query a miner:

```bash
nc localhost 4048
```

Then type:
```
summary
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
