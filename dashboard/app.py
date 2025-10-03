import os
import time
import threading
import socket
import json
from collections import deque
from datetime import datetime
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="templates")

# Config from env
MINERS = os.getenv("MINERS", "localhost:4048").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
HISTORY_SAMPLES = int(os.getenv("HISTORY_SAMPLES", "120"))
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", "").strip()

# In-memory store: per-miner deque of samples
history = {}
status = {}
lock = threading.Lock()

for m in MINERS:
    m = m.strip()
    if m:
        history[m] = deque(maxlen=HISTORY_SAMPLES)
        status[m] = {"online": False, "last_seen": None}


def format_hashrate_from_khs(khs):
    """Convert KHS to H/s"""
    try:
        h = float(khs) * 1000.0
    except Exception:
        return 0.0
    return h


def query_miner_socket(host, port, timeout=2):
    """Talk to cpuminer-opt API via raw TCP socket"""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout) as sock:
            sock.sendall(b'{"id":1,"method":"summary"}\n')
            data = sock.recv(8192).decode("utf-8").strip()
            return json.loads(data)
    except Exception as e:
        return {"error": str(e)}


def poll_miner(endpoint):
    try:
        host, port = endpoint.split(":")
        data = query_miner_socket(host, port)
        if "error" in data:
            raise Exception(data["error"])

        # cpuminer-opt typical keys: KHS (KH/s), ACC, REJ, BEST, UPTIME
        khs = data.get("KHS", 0)
        hashrate_hs = format_hashrate_from_khs(khs)
        acc = int(data.get("ACC", 0))
        rej = int(data.get("REJ", 0))
        best = data.get("BEST", 0)
        uptime = int(data.get("UPTIME", 0))

        sample = {
            "ts": int(time.time()),
            "hashrate_hs": hashrate_hs,
            "accepted": acc,
            "rejected": rej,
            "best": best,
            "uptime": uptime
        }

        with lock:
            history[endpoint].append(sample)
            status[endpoint]["online"] = True
            status[endpoint]["last_seen"] = datetime.utcnow().isoformat() + "Z"

        return sample
    except Exception:
        with lock:
            status[endpoint]["online"] = False
        return None


def poll_loop():
    while True:
        for m in MINERS:
            m = m.strip()
            if not m:
                continue
            poll_miner(m)
        time.sleep(POLL_INTERVAL)


@app.route("/api/miners")
def api_miners():
    """Return current snapshot + short history"""
    with lock:
        out = {}
        for m in MINERS:
            m = m.strip()
            hist = list(history.get(m, []))
            latest = hist[-1] if hist else None
            out[m] = {
                "status": status.get(m, {}),
                "latest": latest,
                "history": hist
            }
    return jsonify(out)


@app.route("/")
def index():
    return render_template("index.html", miners=MINERS, poll_interval=POLL_INTERVAL)


# Simple alerter (optional webhook)
import requests
def send_alert(msg):
    if not ALERT_WEBHOOK:
        return
    try:
        requests.post(ALERT_WEBHOOK, json={"text": msg}, timeout=3)
    except Exception:
        pass


# Health watcher thread: send alerts when status toggles
def watcher_loop():
    prev_online = {m: False for m in MINERS}
    while True:
        with lock:
            for m in MINERS:
                m = m.strip()
                online = status.get(m, {}).get("online", False)
                if online != prev_online.get(m, False):
                    if not online:
                        send_alert(f"[ALERT] Miner {m} went OFFLINE at {datetime.utcnow().isoformat()}Z")
                    else:
                        send_alert(f"[RECOVER] Miner {m} is ONLINE at {datetime.utcnow().isoformat()}Z")
                prev_online[m] = online
        time.sleep(5)


# Start background threads
t = threading.Thread(target=poll_loop, daemon=True)
t.start()
w = threading.Thread(target=watcher_loop, daemon=True)
w.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

