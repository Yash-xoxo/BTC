# ⛏ Bitcoin Lottery Miner Dashboard

A **multi-rig monitoring stack** for Bitcoin solo mining with cpuminer-opt. This project runs multiple CPU miners and a live dashboard to track hashrate, shares, uptime, and lottery odds.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-required-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-green.svg)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Why Docker?](#-why-docker)
- [Why Python?](#-why-python)
- [Architecture](#architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Security Considerations](#security-considerations)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

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

## Prerequisites

- **Docker** (v20.10+) and **Docker Compose** (v2.0+)
- **2+ CPU cores** (more cores = higher hashrate)
- **Valid Bitcoin wallet address** (starts with `bc1...` for SegWit)
- **Stable internet connection**
- **Linux/macOS/Windows** with Docker Desktop

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
git clone https://github.com/yourusername/bitcoin-lottery-miner.git
cd bitcoin-lottery-miner
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

## Advanced Configuration

### Using a Different Mining Pool

Edit `docker-compose.yml`:

```yaml
-o stratum+tcp://your-pool.com:3333
-u YourUsername.WorkerName
-p YourPassword
```

### Adding Prometheus Metrics

Extend `app.py` to expose `/metrics` endpoint for Prometheus scraping.

### Email Alerts

Install `smtplib` and add alert logic when miner goes offline:

```python
import smtplib

def send_alert(miner_name):
    # Send email notification
    pass
```

---

## Security Considerations

⚠️ **Do NOT expose ports publicly** – Miners and dashboard should only be accessible on localhost or via VPN.

- **Firewall Rules:** Block external access to ports 4048, 4049, 5000
- **Use Reverse Proxy:** Deploy Nginx with SSL for secure remote access
- **API Authentication:** Add basic auth to Flask endpoints if exposing remotely

Example Nginx config:

```nginx
server {
    listen 443 ssl;
    server_name mining.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

---

## FAQ

**Q: Can I actually mine Bitcoin with this?**  
A: Technically yes, but the odds of finding a block are astronomically low (~1 in billions). This is educational.

**Q: How much Bitcoin will I earn?**  
A: Realistically, **$0**. CPU mining Bitcoin is not profitable. ASIC miners dominate the network.

**Q: Can I use GPU instead of CPU?**  
A: cpuminer-opt is CPU-only. For GPU mining, use cgminer or similar (but still unprofitable for Bitcoin).

**Q: Why solo mining?**  
A: Pools distribute rewards based on contributed hashrate. Solo mining means you win the full block reward (6.25 BTC) if you find a block—but the odds are infinitesimal.

**Q: Can I run this on a Raspberry Pi?**  
A: Yes, but hashrate will be extremely low (~100 kH/s). Not recommended.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## Disclaimer

**⚠️ EDUCATIONAL USE ONLY**

This software is provided for **educational and experimental purposes only**. Solo mining Bitcoin with CPU hardware has an **extremely low probability** of success and will **not generate meaningful income**.

- **No warranties:** This software is provided "as is" without warranty of any kind.
- **Electricity costs:** Mining consumes electricity. You will likely spend more on power than you earn.
- **Hardware wear:** Continuous mining can shorten hardware lifespan.
- **Use at your own risk:** The authors are not responsible for any losses, damages, or issues arising from use of this software.

**By using this software, you acknowledge that:**
- You understand the economics of Bitcoin mining
- You are using this for learning/experimentation, not profit
- You will not hold the authors liable for any outcomes

---

## Acknowledgments

- **cpuminer-opt** by [JayDDee](https://github.com/JayDDee/cpuminer-opt)
- **solo.ckpool.org** by [Con Kolivas](https://github.com/ckolivas/ckpool)
- **Flask** by the [Pallets Project](https://palletsprojects.com/)
- **Docker** by [Docker Inc.](https://www.docker.com/)

---

## Support

For issues, questions, or feature requests:

- **GitHub Issues:** [Open an issue](https://github.com/yourusername/bitcoin-lottery-miner/issues)
- **Documentation:** Check the [Wiki](https://github.com/yourusername/bitcoin-lottery-miner/wiki)
- **Community:** Join discussions in the [Discussions tab](https://github.com/yourusername/bitcoin-lottery-miner/discussions)

---

**Happy Mining! ⛏️** (Even if it's just for fun and learning)