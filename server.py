"""
Bengaluru Living Agent Metropolis OS: Unified Web Dashboard & 24/7 City Runner (Port 9090)
- 100 Autonomous Citizens executing concurrently across 16 Iconic Bengaluru Sectors
- HTML5 Canvas 2D Spatial Map of Bengaluru with Moving Metro Trains & Live Speech Bubbles
- Living Bengaluru Economy (₹ INR GDP, Metro Fares, Tech Bounties, Cafe Food Expenses)
- BLR-TECH-30 Stock Market Ticker & Startup Valuation Tracker
- Dynamic Bengaluru Weather (22°C Breeze, Monsoons) & Silk Board Congestion Index
- Namma Radio 91.1 FM Live Broadcast Stream (RJ Disha & RJ Raaj)
- City Governor "God Mode" Console (Broadcast, Direct Citizen Calling & Macro Triggers)
- The Bengaluru Chronicle Newsroom Tabloid & Municipal Civic Voting
"""

import os
import sys
import json
import time
import threading
import signal
import atexit
import socket
import gzip
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from typing import Any, Dict, List, Set, Optional

try:
    from ray_agent_world.world_engine import (
        LivingWorld, WORKSPACE_DIR, ZONE_COORDINATES, ZONE_METADATA, 
        METRO_LINES, BENGALURU_ZONES, INITIAL_STOCKS, WEATHER_STATES, CITY_BILLS
    )
except ModuleNotFoundError:
    from world_engine import (
        LivingWorld, WORKSPACE_DIR, ZONE_COORDINATES, ZONE_METADATA, 
        METRO_LINES, BENGALURU_ZONES, INITIAL_STOCKS, WEATHER_STATES, CITY_BILLS
    )

WORLD = LivingWorld()
WORLD_LOCK = threading.Lock()

# Initialize telemetry directly from world step
LAST_TELEMETRY = WORLD.step()
LAST_TELEMETRY_BYTES = b"{}"
LAST_TELEMETRY_GZIP = b""
LAST_TELEMETRY_SSE = b""
WORKSPACE_CACHE = {"timestamp": 0.0, "data": {}}

def update_telemetry_cache(data):
    global LAST_TELEMETRY_BYTES, LAST_TELEMETRY_GZIP, LAST_TELEMETRY_SSE
    try:
        raw = json.dumps(data).encode("utf-8")
        gz = gzip.compress(raw, compresslevel=6)
        sse = ("data: " + json.dumps(data) + "\n\n").encode("utf-8")
        with WORLD_LOCK:
            LAST_TELEMETRY_BYTES = raw
            LAST_TELEMETRY_GZIP = gz
            LAST_TELEMETRY_SSE = sse
    except Exception as e:
        print(f"✗ [Cache Error] {e}")

update_telemetry_cache(LAST_TELEMETRY)

AUTO_RUNNING = True
TICK_INTERVAL_SEC = 3.5

# PID and Advisory Process Lock Management
PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.pid")
SHUTDOWN_EVENT = threading.Event()
CURRENT_SERVER = None

def acquire_pid_lock(pid_file: str) -> bool:
    """Acquire single-instance lock; cleans up stale PID files from crashed instances."""
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                content = f.read().strip()
                if content:
                    old_pid = int(content)
                    if old_pid != os.getpid():
                        try:
                            os.kill(old_pid, 0)
                            print(f"✗ [Bengaluru OS] Another simulator instance is running with PID {old_pid}.")
                            return False
                        except OSError:
                            print(f"✓ [Bengaluru OS] Cleaned up stale PID file from crashed process {old_pid}.")
                            os.remove(pid_file)
        except Exception:
            try:
                os.remove(pid_file)
            except Exception:
                pass

    try:
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"✗ [Bengaluru OS] Failed to write PID file {pid_file}: {e}")
        return False

def release_pid_lock(pid_file: str):
    """Release and delete the PID file on clean shutdown."""
    try:
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                content = f.read().strip()
                if content and int(content) == os.getpid():
                    os.remove(pid_file)
    except Exception:
        pass

def handle_shutdown_signal(signum, frame):
    """Graceful SIGINT/SIGTERM termination handler."""
    sig_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    print(f"\n⚡ [Bengaluru OS] Received {sig_name}. Initiating graceful shutdown...")
    global AUTO_RUNNING
    AUTO_RUNNING = False
    SHUTDOWN_EVENT.set()

    # Notify all SSE clients
    try:
        shutdown_frame = ("data: " + json.dumps({"status": "SHUTDOWN", "message": "Simulator shutting down cleanly"}) + "\n\n").encode()
        with SSE_LOCK:
            for q in list(SSE_SUBSCRIBERS):
                try:
                    q.put_nowait(shutdown_frame)
                except Exception:
                    pass
    except Exception:
        pass

    release_pid_lock(PID_FILE)
    if CURRENT_SERVER:
        threading.Thread(target=CURRENT_SERVER.shutdown, daemon=True).start()

# SSE subscribers — list of queue.Queue objects, one per connected client
import queue as _queue
SSE_SUBSCRIBERS: list = []
SSE_LOCK = threading.Lock()

def _push_sse(data: dict):
    """Push telemetry snapshot to all SSE subscribers with automatic broken-pipe eviction."""
    global LAST_TELEMETRY_SSE
    if data is LAST_TELEMETRY and LAST_TELEMETRY_SSE:
        encoded = LAST_TELEMETRY_SSE
    else:
        encoded = ("data: " + json.dumps(data) + "\n\n").encode()
    dead = []
    with SSE_LOCK:
        for q in list(SSE_SUBSCRIBERS):
            try:
                q.put_nowait(encoded)
            except Exception:
                dead.append(q)
        for q in dead:
            if q in SSE_SUBSCRIBERS:
                SSE_SUBSCRIBERS.remove(q)

def background_autonomous_runner():
    """24/7 Background daemon simulating Bengaluru metropolis."""
    global LAST_TELEMETRY, AUTO_RUNNING
    print(f"⚡ [Bengaluru OS] 100-Citizen simulation active. Stepping every {TICK_INTERVAL_SEC}s.")
    while not SHUTDOWN_EVENT.is_set():
        if AUTO_RUNNING:
            try:
                new_data = WORLD.step()
                with WORLD_LOCK:
                    LAST_TELEMETRY = new_data
                update_telemetry_cache(new_data)
                print(f"✓ [Bengaluru OS] Tick #{LAST_TELEMETRY['tick']} | {LAST_TELEMETRY['world_time']} ({LAST_TELEMETRY['circadian_phase']}) | Dialogues: {len(LAST_TELEMETRY['active_conversations'])} | GDP: {LAST_TELEMETRY['economy']['total_gdp_inr']} | BLR-TECH: {LAST_TELEMETRY['blr_tech_index']}")
                _push_sse(new_data)
                
                # Granular sleep to immediately respond to shutdown signals
                sleep_slices = int(TICK_INTERVAL_SEC * 10)
                for _ in range(sleep_slices):
                    if SHUTDOWN_EVENT.is_set():
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"✗ [Bengaluru OS] Tick Error: {e}")
                time.sleep(2)
        else:
            time.sleep(1)
    print("✓ [Bengaluru OS] Autonomous daemon cleanly terminated.")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bengaluru Living Agent Metropolis OS — 100 Autonomous Citizens</title>
    <style>
        :root {
            --bg: #06090e;
            --card: #0d1522;
            --card-border: rgba(56, 189, 248, 0.22);
            --border: #1e293b;
            --cyan: #00f5ff;
            --cyan-glow: 0 0 14px rgba(0, 245, 255, 0.55);
            --blue: #38bdf8;
            --green: #10b981;
            --green-glow: 0 0 14px rgba(16, 185, 129, 0.55);
            --purple: #c084fc;
            --purple-glow: 0 0 14px rgba(192, 132, 252, 0.55);
            --yellow: #f59e0b;
            --orange: #f97316;
            --red: #f43f5e;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "JetBrains Mono", monospace; }
        body {
            background: radial-gradient(circle at 50% 0%, #0d1728 0%, #06090e 75%);
            color: #f8fafc;
            padding: 16px 20px;
            min-height: 100vh;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(56, 189, 248, 0.25);
            background: rgba(13, 21, 34, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }
        .title { font-size: 20px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; letter-spacing: 0.5px; }
        .live-dot { width: 10px; height: 10px; background: var(--green); border-radius: 50%; display: inline-block; box-shadow: 0 0 14px var(--green); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } 100% { opacity: 1; transform: scale(1); } }
        
        .badge-city {
            background: rgba(249, 115, 22, 0.15);
            border: 1px solid var(--orange);
            color: var(--orange);
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(249, 115, 22, 0.2);
        }
        .badge-clock {
            background: rgba(0, 245, 255, 0.12);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 6px;
            box-shadow: 0 0 12px rgba(0, 245, 255, 0.2);
            font-family: 'JetBrains Mono', monospace;
        }
        .badge-weather {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid var(--yellow);
            color: var(--yellow);
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
        }

        /* Stock Market Ribbon */
        .stock-ribbon {
            display: flex;
            background: rgba(10, 16, 28, 0.85);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 14px;
            gap: 16px;
            overflow-x: auto;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        }
        .stock-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            white-space: nowrap;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 3px 8px;
            border-radius: 6px;
        }
        .stock-sym { font-weight: bold; color: #fff; letter-spacing: 0.5px; }
        .stock-val { color: #e2e8f0; font-family: 'JetBrains Mono', monospace; }
        .stock-up { color: var(--green); font-size: 11px; font-weight: bold; text-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
        .stock-down { color: var(--red); font-size: 11px; font-weight: bold; text-shadow: 0 0 8px rgba(244, 63, 94, 0.4); }

        .grid-metrics {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }
        .metric-card {
            background: rgba(13, 21, 34, 0.82);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 10px 14px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0, 245, 255, 0.5);
            box-shadow: 0 8px 25px rgba(0, 245, 255, 0.15);
        }
        .metric-label { font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; }
        .metric-value { font-size: 19px; font-weight: bold; color: #fff; margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

        .canvas-container {
            position: relative;
            width: 100%;
            height: 500px;
            background: #06090e;
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 245, 255, 0.1);
        }
        #bengaluru-canvas { width: 100%; height: 100%; display: block; }

        .god-mode-bar {
            background: #101620;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .god-row {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .god-input {
            flex: 1;
            min-width: 250px;
            background: #070a0f;
            border: 1px solid var(--border);
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }
        .god-select {
            background: #070a0f;
            border: 1px solid var(--border);
            color: #c9d1d9;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 12px;
            max-width: 280px;
        }

        .macro-btn {
            background: #1a2332;
            border: 1px solid #233042;
            color: #c9d1d9;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .macro-btn:hover {
            background: #233042;
            color: #fff;
            border-color: var(--cyan);
        }

        .main-layout {
            display: grid;
            grid-template-columns: 1.25fr 1fr;
            gap: 16px;
        }
        .section-box {
            background: var(--card);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 16px;
        }
        .section-header { 
            font-size: 13px; 
            font-weight: 700; 
            color: #fff; 
            margin-bottom: 10px; 
            border-bottom: 1px solid var(--border); 
            padding-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .radio-card {
            background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(188, 140, 255, 0.1));
            border: 1px solid rgba(88, 166, 255, 0.3);
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 12px;
            font-size: 12px;
        }
        .radio-title { font-weight: bold; color: var(--cyan); display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }

        .dialogue-item {
            background: #090e15;
            border-left: 3px solid var(--purple);
            padding: 8px 12px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 10px;
            font-size: 12px;
        }
        .dialogue-meta { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }
        .dialogue-turn { margin-top: 3px; }
        .speaker-name { font-weight: bold; color: var(--cyan); }

        .feed-box {
            max-height: 230px;
            overflow-y: auto;
        }

        .bill-card {
            background: #090e15;
            border: 1px solid var(--card-border);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
            font-size: 12px;
        }
        .bill-title { font-weight: bold; color: #fff; display: flex; justify-content: space-between; }
        .bill-status { font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        .status-voting { background: rgba(227, 179, 65, 0.2); color: var(--yellow); border: 1px solid var(--yellow); }
        .status-passed { background: rgba(63, 185, 80, 0.2); color: var(--green); border: 1px solid var(--green); }

        .workspace-card {
            background: #090e15;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
            font-size: 11px;
            font-family: monospace;
        }

        .desktop-preview {
            width: 100%;
            border-radius: 6px;
            border: 1px solid var(--border);
        }

        .btn {
            background: #238636;
            color: #fff;
            border: none;
            padding: 7px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            white-space: nowrap;
        }
        .btn:hover { background: #2ea043; }
        .btn-blue { background: #1f6feb; }
        .btn-blue:hover { background: #388bfd; }
        .btn-pause { background: #6e7681; }

        /* Citizen Directory Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            background: var(--card);
            border: 1px solid var(--orange);
            border-radius: 8px;
            width: 600px;
            max-width: 90%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        .citizen-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            overflow-y: auto;
            max-height: 60vh;
            margin-top: 12px;
            padding-right: 6px;
        }
        .citizen-mini-card {
            background: #090e15;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .citizen-mini-card:hover { border-color: var(--cyan); background: #111a24; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.js"></script>
    <script src="/static/voxel_3d_engine.js"></script>
</head>
<body>
    <div class="header">
        <div class="title">
            <span class="live-dot"></span>
            BENGALURU LIVING AGENT METROPOLIS OS
            <span class="badge-city">NAMMA BENGALURU</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <div class="badge-weather" id="b-weather">23°C • Gentle Breeze</div>
            <div class="badge-clock" id="world-clock">Day 1 • 09:15 AM</div>
            <div class="badge-circadian" id="circadian-badge" style="background: rgba(188, 140, 255, 0.15); border: 1px solid var(--purple); color: var(--purple); font-size: 12px; font-weight: bold; padding: 4px 10px; border-radius: 6px; display: flex; align-items: center; gap: 5px;">
                <span id="circadian-icon">☀️</span> <span id="circadian-text">Morning Standup</span>
            </div>
            <button class="btn btn-blue" onclick="openDirectoryModal()" style="padding: 4px 10px; font-size: 11px;">👥 100 Citizens</button>
            <button id="voice-toggle-btn" class="btn" onclick="toggleVoice()" style="padding: 4px 10px; font-size: 11px; background: #1e293b; border: 1px solid #38bdf8; color: #38bdf8;">🔊 Voice: ON</button>
            <button class="btn" onclick="openCitizenCallModal()" style="padding: 4px 10px; font-size: 11px; background: #064e3b; border: 1px solid #10b981; color: #10b981;">📞 Call Citizen</button>
        </div>
    </div>

    <!-- 24h Circadian Time Warp & Instant Step Controller -->
    <div style="display: flex; justify-content: space-between; align-items: center; background: #0c121d; border: 1px solid var(--card-border); border-radius: 6px; padding: 6px 12px; margin-bottom: 12px; gap: 8px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 11px; font-weight: bold; color: var(--cyan); text-transform: uppercase;">⏱️ 24h Circadian Cycle:</span>
            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                <button class="macro-btn" onclick="warpTime(1, 0)" title="Warp to 01:00 AM Midnight">🌙 Midnight (01:00 AM)</button>
                <button class="macro-btn" onclick="warpTime(5, 30)" title="Warp to 05:30 AM Early Dawn">🌅 Early Morning (05:30 AM)</button>
                <button class="macro-btn" onclick="warpTime(9, 30)" title="Warp to 09:30 AM Morning">☀️ Morning (09:30 AM)</button>
                <button class="macro-btn" onclick="warpTime(14, 0)" title="Warp to 02:00 PM Afternoon">🥪 Afternoon (02:00 PM)</button>
                <button class="macro-btn" onclick="warpTime(18, 45)" title="Warp to 06:45 PM Twilight">🌆 Evening (06:45 PM)</button>
                <button class="macro-btn" onclick="warpTime(22, 15)" title="Warp to 10:15 PM Starlit Night">🍺 Night (10:15 PM)</button>
            </div>
        </div>
        <div style="display: flex; gap: 6px; align-items: center;">
            <button class="macro-btn" onclick="stepSimNow()" style="background: rgba(63, 185, 80, 0.15); border-color: var(--green); color: var(--green); font-weight: bold;" title="Advance time by 1 tick (+15 mins) immediately">⚡ Step (+15m)</button>
        </div>
    </div>

    <!-- BLR-TECH-30 Stock Market Ribbon -->
    <div class="stock-ribbon" id="stock-ribbon">
        <span style="color: var(--orange); font-weight: bold; font-size: 11px; text-transform: uppercase;">📈 BLR-TECH-30:</span>
        <div id="stock-items" style="display: flex; gap: 14px;"></div>
    </div>

    <div class="grid-metrics">
        <div class="metric-card">
            <div class="metric-label">Autonomous Citizens</div>
            <div class="metric-value" id="m-count" style="color: var(--cyan);">100 Active</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">City GDP (₹ INR)</div>
            <div class="metric-value" id="m-gdp" style="color: var(--green);">₹2,500,000</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">BLR-TECH Index</div>
            <div class="metric-value" id="m-index" style="color: var(--purple);">26,980.50</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Silk Board Bottleneck</div>
            <div class="metric-value" id="m-silk" style="color: var(--red);">78% Gridlock</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Spoken Dialogues</div>
            <div class="metric-value" id="m-convs" style="color: var(--yellow);">0 Recorded</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Average Stamina</div>
            <div class="metric-value" id="m-energy">98.5%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">🧱 Voxel Blocks Built</div>
            <div class="metric-value" id="m-blocks" style="color: #10b981;">0 Blocks</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">💼 P2P Contracts Active</div>
            <div class="metric-value" id="m-bounties" style="color: #38bdf8;">0 Open</div>
        </div>
    </div>

    <!-- 3D Minecraft Voxel Metropolis & 2D Radar Dual Viewport -->
    <div style="display: flex; justify-content: space-between; align-items: center; background: #0f172a; padding: 8px 14px; border: 1px solid var(--border); border-radius: 8px 8px 0 0; margin-bottom: -1px;">
        <div style="display: flex; gap: 8px; align-items: center;">
            <span style="font-weight: bold; font-size: 12px; color: var(--orange);">🎮 VIEWPORT:</span>
            <button id="btn-view-3d" class="btn btn-blue" onclick="switchViewMode('3d')" style="padding: 4px 12px; font-size: 11px;">🧊 3D Minecraft Voxel Metropolis</button>
            <button id="btn-view-2d" class="btn" onclick="switchViewMode('2d')" style="padding: 4px 12px; font-size: 11px; background: #1e293b; color: #94a3b8;">🗺️ 2D Strategic Radar</button>
        </div>
        <div id="controls-hint-3d" style="font-size: 11px; color: #94a3b8; display: flex; gap: 14px;">
            <span>🕹️ <strong style="color: #fff;">[W][A][S][D]:</strong> Walk Governor Avatar</span>
            <span>🖱️ <strong style="color: #fff;">Drag:</strong> 360° Orbit</span>
            <span>🔍 <strong style="color: #fff;">Scroll:</strong> Zoom</span>
            <span>🎥 <strong style="color: #fff;">[C]:</strong> Toggle 3rd-Person Follow</span>
            <span>📞 <strong style="color: #38bdf8;">Click Citizen:</strong> Direct Intercom Call</span>
        </div>
    </div>
    <div class="canvas-container" id="canvas-wrapper" style="position: relative; height: 680px; margin-bottom: 16px; border-radius: 0 0 8px 8px;">
        <div id="threejs-container" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 2;"></div>
        <!-- Autopolis-Style Glassmorphic Monospace HUD Header (Top Left) -->
        <div id="autopolis-hud-header" style="position: absolute; top: 14px; left: 14px; z-index: 10; background: rgba(8, 14, 26, 0.88); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(0, 245, 255, 0.5); box-shadow: 0 0 25px rgba(0, 245, 255, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px 14px; font-family: 'JetBrains Mono', monospace; pointer-events: auto;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00ff66; box-shadow: 0 0 10px #00ff66;"></span>
                <span style="font-size: 11px; font-weight: 800; color: #00f5ff; letter-spacing: 0.8px;">BENGALURU METROPOLIS OS // 100 CITIZENS</span>
            </div>
            <div style="font-size: 9px; color: #94a3b8; margin-top: 3px; letter-spacing: 0.5px;">16 SECTORS • 3 METRO LINES • 100K+ GLOWING WINDOWS • 60 FPS</div>
        </div>

        <!-- Autopolis-Style Glassmorphic Telemetry Card (Top Right) -->
        <div id="autopolis-hud-telemetry" style="position: absolute; top: 14px; right: 230px; z-index: 10; background: rgba(8, 14, 26, 0.88); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 0, 127, 0.45); box-shadow: 0 0 25px rgba(255, 0, 127, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px 14px; font-family: 'JetBrains Mono', monospace; text-align: right; pointer-events: auto;">
            <div style="font-size: 11px; font-weight: 700; color: #ff007f;" id="hud-time-phase">DAY 1 • 10:45 AM // MORNING STANDUP</div>
            <div style="font-size: 9px; color: #cbd5e1; margin-top: 3px;" id="hud-stats-summary">38 DESKS • 16 CLASS • 14 CAFES • 8 PUBS • 54 BEACONS</div>
        </div>

        <!-- Center Cinematic Cue Card (Autopolis Signature) -->
        <div id="autopolis-cue-card" style="position: absolute; bottom: 32px; left: 50%; transform: translateX(-50%); z-index: 10; background: rgba(10, 15, 28, 0.88); backdrop-filter: blur(14px); border: 1px solid rgba(0, 245, 255, 0.6); box-shadow: 0 0 25px rgba(0, 245, 255, 0.25); border-radius: 8px; padding: 9px 22px; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #f8fafc; letter-spacing: 0.8px; transition: all 0.4s ease; pointer-events: none; opacity: 1;">
            Then I let them run it.
        </div>
        <canvas id="bengaluru-canvas" style="width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; display: none;"></canvas>
        <div id="avatar-proximity-hud" style="position: absolute; bottom: 12px; left: 14px; background: rgba(11, 18, 30, 0.9); border: 1px solid #38bdf8; border-radius: 6px; padding: 6px 12px; font-size: 11px; color: #38bdf8; pointer-events: none; z-index: 10;">🚶 Governor Avatar • WASD to walk • [V] First-Person / Orbit</div>
        <button onclick="if(window.metropolis3D) window.metropolis3D.toggleCameraMode();" class="btn" style="position: absolute; top: 12px; right: 14px; z-index: 10; font-size: 11px; background: rgba(15, 23, 42, 0.88); border: 1px solid #38bdf8; color: #fff; padding: 6px 10px;">🎥 <span id="camera-mode-badge">🌐 ORBIT (God View)</span> [V]</button>

        <!-- Floating Cyber Quick-Bar (Direct 1-Click Fly-Throughs & Night/Day Lighting) -->
        <div id="canvas-quick-toolbar" style="position: absolute; bottom: 12px; right: 14px; z-index: 10; display: flex; gap: 6px; flex-wrap: wrap; background: rgba(8, 14, 26, 0.88); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(56, 189, 248, 0.35); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 245, 255, 0.15); border-radius: 8px; padding: 6px 10px;">
            <button class="btn" style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.85), rgba(3, 105, 161, 0.85)); border: 1px solid #38bdf8; font-size: 11px; font-weight: 700; color: #fff; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) window.metropolis3D.cinematicWindowFlyThrough('Manyata_Tech_Park');">🚀 Manyata</button>
            <button class="btn" style="background: linear-gradient(135deg, rgba(5, 150, 105, 0.85), rgba(4, 120, 87, 0.85)); border: 1px solid #10b981; font-size: 11px; font-weight: 700; color: #fff; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) window.metropolis3D.cinematicWindowFlyThrough('IISc_Research_Campus');">🏫 Academy</button>
            <button class="btn" style="background: linear-gradient(135deg, rgba(217, 119, 6, 0.85), rgba(180, 83, 9, 0.85)); border: 1px solid #f59e0b; font-size: 11px; font-weight: 700; color: #fff; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) window.metropolis3D.cinematicWindowFlyThrough('UB_City_Luxury_Towers');">💎 UB City</button>
            <button class="btn" style="background: linear-gradient(135deg, rgba(147, 51, 234, 0.85), rgba(126, 34, 206, 0.85)); border: 1px solid #c084fc; font-size: 11px; font-weight: 700; color: #fff; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) window.metropolis3D.cinematicWindowFlyThrough('Electronic_City_Phase_1');">🖥️ E-City</button>
            <button class="btn" style="background: rgba(30, 41, 59, 0.9); border: 1px solid #fde047; font-size: 11px; font-weight: 700; color: #fef08a; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) window.metropolis3D.toggleDayNight();">💡 Night / Day</button>
            <button class="btn" style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.85), rgba(2, 132, 199, 0.85)); border: 1px solid #38bdf8; font-size: 11px; font-weight: 700; color: #e0f2fe; padding: 4px 10px; border-radius: 6px;" onclick="if(window.metropolis3D) { const on = window.metropolis3D.toggleStorm(); this.innerText = on ? '⚡ Storm: ON' : '⚡ Storm'; }">⚡ Storm</button>
        </div>
    </div>

    <!-- City Governor "God Mode" Console -->
    <div class="god-mode-bar">
        <div class="god-row">
            <span style="font-size: 12px; font-weight: bold; color: var(--orange); white-space: nowrap;">🏛️ GOVERNOR DIRECTIVES:</span>
            <input type="text" id="god-input" class="god-input" placeholder="Broadcast emergency decree or directive (e.g. 'Audit all cluster servers at Manyata Tech Park')...">
            <select id="god-target" class="god-select">
                <option value="ALL">📢 City-Wide Broadcast (All 100 Citizens)</option>
            </select>
            <button class="btn btn-blue" onclick="sendGodCommand()">Dispatch Decree</button>
            <button class="btn btn-pause" id="btn-toggle" onclick="toggleAuto()">⏸ Pause City</button>
            <button class="btn" onclick="stepManual()">⏩ Step Tick</button>
        </div>
        <div class="god-row" style="border-top: 1px solid var(--card-border); padding-top: 8px;">
            <span style="font-size: 11px; color: var(--text-muted); font-weight: bold;">QUICK MACRO ACTIONS:</span>
            <button class="macro-btn" onclick="triggerMacro('MONSOON_FLOOD')">🌧️ Monsoon Flood Silk Board</button>
            <button class="macro-btn" onclick="triggerMacro('HACKATHON_50CR')">🚀 ₹50Cr Tech Hackathon</button>
            <button class="macro-btn" onclick="triggerMacro('POWER_GRID_DROP')">⚡ E-City Power Blip</button>
            <button class="macro-btn" onclick="triggerMacro('FILTER_COFFEE_DAY')">☕ Free Filter Coffee Day</button>
            <button class="macro-btn" onclick="triggerMacro('AIRPORT_METRO_EXPRESS')">🚇 Airport Metro Express</button>
        </div>
    <!-- REAL-WORLD MACRO-GDP & NATIONAL ACCOUNTING ENGINE (GDP = C + I + G + NX) -->
    <div style="background: linear-gradient(135deg, #090e15 0%, #0d1520 100%); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
            <div style="font-size: 13px; font-weight: bold; color: var(--cyan); display: flex; align-items: center; gap: 8px;">
                <span>🌐 BENGALURU MACRO-GDP & NATIONAL ACCOUNTING ENGINE:</span>
                <span style="background: rgba(34, 197, 94, 0.2); color: var(--green); border: 1px solid var(--green); font-size: 11px; padding: 2px 8px; border-radius: 12px;" id="gdp-headline">₹3,916.51 Cr (+10.7% YoY)</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8;">
                Formula: <strong style="color: #fff;">GDP = C + I + G + NX</strong> • Scaled National Income Model
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; text-align: center;">
            <div style="background: #0d1726; border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🛒 Private Consumption (C)</div>
                <div style="font-size: 13px; font-weight: bold; color: #38bdf8;" id="gdp-c">₹2,151.5 Cr</div>
                <div style="font-size: 9px; color: #64748b;">Cafes, Pubs, Gyms, Retail, Rent</div>
            </div>
            <div style="background: #0d1726; border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">💼 Gross Investment (I)</div>
                <div style="font-size: 13px; font-weight: bold; color: #a78bfa;" id="gdp-i">₹1,011.2 Cr</div>
                <div style="font-size: 9px; color: #64748b;">Startups, Voxel Infra, Hardware</div>
            </div>
            <div style="background: #0d1726; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🏛️ Public Works (G)</div>
                <div style="font-size: 13px; font-weight: bold; color: #f59e0b;" id="gdp-g">₹420.4 Cr</div>
                <div style="font-size: 9px; color: #64748b;">Namma Metro, Roads, Parks</div>
            </div>
            <div style="background: #0d1726; border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🌍 Net Tech Exports (NX)</div>
                <div style="font-size: 13px; font-weight: bold; color: #10b981;" id="gdp-nx">₹300.6 Cr</div>
                <div style="font-size: 9px; color: #64748b;">Global SaaS & AI IP Outflows</div>
            </div>
            <div style="background: #0d1726; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🏦 City Treasury Reserve</div>
                <div style="font-size: 13px; font-weight: bold; color: #f43f5e;" id="gdp-treasury">₹10.65 Cr</div>
                <div style="font-size: 9px; color: #64748b;">10% Civic Tax Collection Pool</div>
            </div>
        </div>
    </div>

    <!-- SYNTHETIC CONSUMER FOCUS GROUP & MARKETING INTELLIGENCE STUDIO -->
    <div style="background: linear-gradient(135deg, #0b111c 0%, #111a28 100%); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px;">
            <div>
                <div style="font-size: 13px; font-weight: bold; color: var(--yellow); display: flex; align-items: center; gap: 8px;">
                    <span>🎯 SYNTHETIC FOCUS GROUP STUDIO & CONSUMER INTELLIGENCE:</span>
                    <span style="background: rgba(245, 158, 11, 0.15); color: var(--orange); border: 1px solid var(--orange); font-size: 10px; padding: 2px 8px; border-radius: 12px;">100 LIVING CONSUMER PERSONAS</span>
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">
                    Bass Diffusion Model <strong style="color: #fff;">dN/dt = [p + q*(N/M)]*(M - N)</strong> • The Wallet Test • Subconscious Thought Monologues • A/B Market Validation
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-blue" onclick="openLaunchCampaignModal()" style="font-size: 11px; padding: 4px 10px;">🚀 Launch Product</button>
                <button class="btn" onclick="openABTestModal()" style="font-size: 11px; padding: 4px 10px; background: #8b5cf6; color: #fff;">⚖️ A/B Split Test</button>
            </div>
        </div>

        <!-- 4 Top Studio KPIs -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; text-align: center;">
            <div style="background: #090e15; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">💰 Total Product Revenue</div>
                <div style="font-size: 14px; font-weight: bold; color: #10b981;" id="mkt-total-revenue">₹0</div>
                <div style="font-size: 9px; color: #64748b;">Diverted to Macro-GDP Consumption (C)</div>
            </div>
            <div style="background: #090e15; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">⭐ Net Promoter Score (NPS)</div>
                <div style="font-size: 14px; font-weight: bold; color: #38bdf8;" id="mkt-avg-nps">+50.0</div>
                <div style="font-size: 9px; color: #64748b;">Promoters (9-10) vs Detractors (1-6)</div>
            </div>
            <div style="background: #090e15; border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🔄 Viral WOM K-Factor</div>
                <div style="font-size: 14px; font-weight: bold; color: #c084fc;" id="mkt-k-factor">1.42x</div>
                <div style="font-size: 9px; color: #64748b;">Viral Diffusion Coefficient (K > 1.0)</div>
            </div>
            <div style="background: #090e15; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 6px;">
                <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">🛡️ The Wallet Test Barrier</div>
                <div style="font-size: 14px; font-weight: bold; color: #f87171;" id="mkt-rejection-rate">25.0%</div>
                <div style="font-size: 9px; color: #64748b;">Solvency & Skepticism Filtered</div>
            </div>
        </div>

        <!-- Studio 3-Column Layout: Campaigns | Objections & Monologues | Interactive Focus Group Interrogator -->
        <div style="display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 12px;">
            <!-- Column 1: Active Product Campaigns & A/B Testing Grid -->
            <div>
                <div style="font-size: 11px; font-weight: bold; color: var(--cyan); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>📦 ACTIVE CAMPAIGNS & BASS DIFFUSION</span>
                    <span style="font-size: 10px; color: #94a3b8;">Click-Through & Conversion</span>
                </div>
                <div id="campaigns-list" style="display: flex; flex-direction: column; gap: 8px; max-height: 280px; overflow-y: auto; padding-right: 4px;"></div>
            </div>

            <!-- Column 2: Objection Taxonomy Breakdown & Subconscious Monologue Feed -->
            <div>
                <div style="font-size: 11px; font-weight: bold; color: #f87171; margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>🧠 SUBCONSCIOUS THOUGHT MONOLOGUES</span>
                    <span style="font-size: 10px; color: #94a3b8;">Unvarnished System-2</span>
                </div>
                <div id="objection-pills" style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 6px; font-size: 10px;"></div>
                <div id="monologue-feed" style="background: #06090e; border: 1px solid var(--border); border-radius: 6px; padding: 8px; max-height: 245px; overflow-y: auto; font-size: 11px; display: flex; flex-direction: column; gap: 6px;"></div>
            </div>

            <!-- Column 3: Interactive Synthetic Focus Group Console -->
            <div>
                <div style="font-size: 11px; font-weight: bold; color: var(--yellow); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>🎙️ INSTANT FOCUS GROUP INTERVIEWER</span>
                    <span style="font-size: 10px; color: #94a3b8;">Ask 100 Personas</span>
                </div>
                <div style="background: #06090e; border: 1px solid var(--border); border-radius: 6px; padding: 10px; display: flex; flex-direction: column; gap: 6px;">
                    <div style="font-size: 10px; color: #94a3b8;">Target Demographic Cohort:</div>
                    <select id="fg-cohort-select" style="background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px 6px; font-size: 11px;">
                        <option value="ALL">All 100 Metropolis Citizens</option>
                        <option value="TECH_FOUNDERS_ARCHITECTS">Tech Founders & Architects (High Skepticism)</option>
                        <option value="HOSPITALITY_ARTISANS">Hospitality, Artisans & Baristas</option>
                        <option value="PARENTS_FAMILIES">Working Parents & Families</option>
                    </select>
                    <div style="font-size: 10px; color: #94a3b8; margin-top: 2px;">Inquiry Question:</div>
                    <input type="text" id="fg-question-input" value="Would you pay ₹2,499 for automated microsecond AI kernel tracing?" style="background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px 6px; font-size: 11px;" />
                    <button class="btn btn-blue" onclick="runSyntheticFocusGroup()" style="font-size: 11px; padding: 6px 10px; margin-top: 4px;">⚡ Interrogate Cohort Subconscious</button>
                    
                    <div id="fg-results-box" style="margin-top: 6px; font-size: 10px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 6px; max-height: 120px; overflow-y: auto;">
                        <div style="color: #64748b; font-style: italic;">Run a focus group to interrogate the 100 citizen personas in real-time.</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- METROPOLIS LIVE TV BROADCAST NETWORK & NAMMA-NET SOCIAL MEDIA SUITE -->
    <div style="display: grid; grid-template-columns: 1.25fr 1fr; gap: 16px; margin-bottom: 16px;">
        <!-- Left Box: 📺 Live Broadcast TV Channels & Teleprompter -->
        <div class="section-box" style="padding: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 13px; font-weight: 800; color: #fff;">📺 METROPOLIS LIVE TV BROADCAST NETWORK</span>
                    <span style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; display: flex; align-items: center; gap: 4px;">
                        <span style="width: 6px; height: 6px; background: #ef4444; border-radius: 50%; display: inline-block;"></span> LIVE ON AIR
                    </span>
                </div>
                <!-- Channel Switcher -->
                <div style="display: flex; gap: 5px;">
                    <button class="macro-btn" id="tv-btn-blr24" onclick="switchTVChannel('BLR24_NEWS')" style="font-size: 10px; padding: 3px 8px; border-color: #ef4444; color: #fca5a5; font-weight: bold;">📺 BLR24</button>
                    <button class="macro-btn" id="tv-btn-cnbc" onclick="switchTVChannel('CNBC_BLR_TECH')" style="font-size: 10px; padding: 3px 8px;">📈 CNBC-BLR</button>
                    <button class="macro-btn" id="tv-btn-ai" onclick="switchTVChannel('METRO_AI_PULSE')" style="font-size: 10px; padding: 3px 8px;">🌐 AI PULSE</button>
                </div>
            </div>

            <!-- TV Screen Frame -->
            <div style="background: #06090e; border: 1px solid #1e293b; border-radius: 6px; padding: 12px; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 11px;">
                    <div>
                        <strong style="color: #fff;" id="tv-show-title">Namma Bengaluru Super Prime</strong>
                        <span style="color: #94a3b8; margin-left: 6px;" id="tv-anchor-name">— Rajeshwari Gowda</span>
                    </div>
                    <div style="font-size: 10px; color: #64748b;" id="tv-studio-loc">MG Road Broadcast Center, Studio A</div>
                </div>

                <!-- Teleprompter / Studio Monologue -->
                <div id="tv-teleprompter" style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid #38bdf8; padding: 10px 12px; border-radius: 4px; font-size: 12px; color: #e2e8f0; font-style: italic; min-height: 48px; line-height: 1.5; margin-bottom: 10px;">
                    Connecting to Bengaluru television broadcast satellites...
                </div>

                <!-- Bottom-Third Breaking News Ticker -->
                <div style="background: #991b1b; color: #fff; padding: 5px 8px; border-radius: 4px; display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: bold; overflow: hidden;">
                    <span style="background: #ef4444; color: #fff; padding: 2px 5px; border-radius: 2px; font-size: 9px; letter-spacing: 0.5px; text-transform: uppercase;">BREAKING</span>
                    <span id="tv-ticker-text" style="color: #fef08a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        Loading live breaking news wire...
                    </span>
                </div>
            </div>

            <!-- Real-Time Public Web Intel Bar -->
            <div style="margin-top: 10px; background: #090e17; border: 1px solid var(--border); border-radius: 6px; padding: 8px 10px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 10px;">
                <div>
                    <span style="color: #94a3b8;">🛰️ Live Open-Meteo Weather:</span><br>
                    <strong style="color: #38bdf8;" id="real-weather-val">12.97°N • 28.5°C Live</strong>
                </div>
                <div>
                    <span style="color: #94a3b8;">💵 Live Forex Rate:</span><br>
                    <strong style="color: #10b981;" id="real-forex-val">₹86.85 / USD</strong>
                </div>
                <div>
                    <span style="color: #94a3b8;">🔥 Hacker News Wire:</span><br>
                    <strong style="color: #f59e0b;" id="real-hn-val">OpenAI agentic safety</strong>
                </div>
            </div>
        </div>

        <!-- Right Box: 🌐 NAMMA-NET: Social Media & Community Groups -->
        <div class="section-box" style="padding: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <span style="font-size: 13px; font-weight: 800; color: #fff;">🌐 NAMMA-NET: SOCIAL & COMMUNITY</span>
                <div style="display: flex; gap: 4px;">
                    <button class="macro-btn" id="social-tab-pulse" onclick="switchSocialTab('pulse')" style="font-size: 10px; padding: 3px 8px; border-color: #38bdf8; color: #38bdf8; font-weight: bold;">🐦 BLR Pulse</button>
                    <button class="macro-btn" id="social-tab-groups" onclick="switchSocialTab('groups')" style="font-size: 10px; padding: 3px 8px;">👥 Groups</button>
                    <button class="macro-btn" id="social-tab-reddit" onclick="switchSocialTab('reddit')" style="font-size: 10px; padding: 3px 8px;">👽 r/bangalore</button>
                    <button class="macro-btn" id="social-tab-places" onclick="switchSocialTab('places')" style="font-size: 10px; padding: 3px 8px;">🛕 Places</button>
                </div>
            </div>

            <!-- Tab 1: BLR Pulse (X/Twitter) -->
            <div id="panel-social-pulse">
                <!-- Tweet Composer as Governor -->
                <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                    <input type="text" id="gov-tweet-input" placeholder="Post live tweet as Governor (@Governor_Lalith)..." style="flex: 1; background: #070a0f; border: 1px solid var(--border); color: #fff; padding: 6px 10px; border-radius: 4px; font-size: 11px;" />
                    <button class="btn btn-blue" onclick="postGovernorTweet()" style="font-size: 10px; padding: 6px 10px;">Post 🚀</button>
                </div>
                <!-- Trending Hashtags Pills -->
                <div id="social-trends-bar" style="display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 8px; font-size: 10px;"></div>
                <!-- Tweet Feed -->
                <div id="social-tweets-feed" style="max-height: 190px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;"></div>
            </div>

            <!-- Tab 2: Community Groups -->
            <div id="panel-social-groups" style="display: none; max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
                <div id="community-groups-list" style="display: flex; flex-direction: column; gap: 6px;"></div>
            </div>

            <!-- Tab 3: r/bangalore Reddit -->
            <div id="panel-social-reddit" style="display: none; max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
                <div id="reddit-threads-list" style="display: flex; flex-direction: column; gap: 6px;"></div>
            </div>

            <!-- Tab 4: Places of Worship, Housing & Care -->
            <div id="panel-social-places" style="display: none; max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px;">
                <div id="community-places-list" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;"></div>
            </div>
        </div>
    </div>

    <!-- REAL-WORLD LIVING ECOSYSTEM: DEDICATED HOUSES, SMARTPHONES & FAUNA -->
    <div style="display: grid; grid-template-columns: 1.15fr 1fr 1.15fr; gap: 14px; margin-bottom: 16px;">
        <!-- CARD 1: 🏡 DEDICATED HOUSING & RESIDENTIAL LEASES -->
        <div class="section-box" style="padding: 14px; background: #0c121e; border: 1px solid rgba(56, 189, 248, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
                <div style="font-size: 13px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
                    <span>🏡 DEDICATED HOUSING & RESIDENTIAL LEASES</span>
                    <span style="font-size: 10px; background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 1px 6px; border-radius: 10px;">100/100 HOMES</span>
                </div>
                <button class="macro-btn" onclick="openCitizenHousingModal('c1')" style="font-size: 10px; padding: 2px 8px; border-color: #38bdf8; color: #38bdf8;">🔑 Inspect Homes</button>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 10px; text-align: center;">
                <div style="background: #070c14; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;">
                    <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">At Home</div>
                    <div style="font-size: 13px; font-weight: bold; color: #38bdf8;" id="house-at-home">0</div>
                </div>
                <div style="background: #070c14; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;">
                    <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">In Bed Sleeping</div>
                    <div style="font-size: 13px; font-weight: bold; color: #c084fc;" id="house-sleeping">0</div>
                </div>
                <div style="background: #070c14; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;">
                    <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">Rent Collected</div>
                    <div style="font-size: 13px; font-weight: bold; color: #10b981;" id="house-rent">₹0.00</div>
                </div>
            </div>
            <div style="font-size: 11px; font-weight: bold; color: #94a3b8; margin-bottom: 4px;">Top Residential Complexes & PGs:</div>
            <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.5; max-height: 110px; overflow-y: auto;" id="housing-complexes-list">
                <div>🏘️ <strong>Dev Co-Living PG</strong> (Indiranagar) • ₹14,500/mo • 14 Residents</div>
                <div>🏡 <strong>Sobha Daisy Society</strong> (HSR Layout) • ₹38,000/mo • 18 Residents</div>
                <div>🛕 <strong>Basavanagudi Heritage Houses</strong> • ₹28,000/mo • 12 Residents</div>
                <div>🏢 <strong>Prestige Ozone Towers</strong> (Whitefield) • ₹45,000/mo • 16 Residents</div>
                <div>☁️ <strong>Manyata Cloud Residency</strong> (Hebbal) • ₹24,000/mo • 14 Residents</div>
            </div>
            <div id="housing-event-log" style="margin-top: 8px; font-size: 10px; color: #38bdf8; font-style: italic; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 5px;">
                Citizens commute home during night & midnight phases to recharge energy to 100%.
            </div>
        </div>

        <!-- CARD 2: 📱 CITIZEN SMARTPHONES & DIGITAL UPI -->
        <div class="section-box" style="padding: 14px; background: #0c121e; border: 1px solid rgba(16, 185, 129, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
                <div style="font-size: 13px; font-weight: 800; color: #10b981; display: flex; align-items: center; gap: 6px;">
                    <span>📱 CITIZEN SMARTPHONES & UPI</span>
                    <span style="font-size: 10px; background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 1px 6px; border-radius: 10px;">5G CONNECTED</span>
                </div>
                <button class="macro-btn" onclick="openCitizenPhoneModal('c1')" style="font-size: 10px; padding: 2px 8px; border-color: #10b981; color: #10b981;">📱 Open Phone</button>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px; text-align: center;">
                <div style="background: #070c14; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;">
                    <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">Active Handsets</div>
                    <div style="font-size: 13px; font-weight: bold; color: #10b981;" id="phone-count">100 / 100</div>
                </div>
                <div style="background: #070c14; border: 1px solid #1e293b; border-radius: 6px; padding: 6px;">
                    <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase;">UPI Digital Volume</div>
                    <div style="font-size: 13px; font-weight: bold; color: #fbbf24;" id="phone-upi-vol">₹0.00</div>
                </div>
            </div>
            <div style="font-size: 11px; font-weight: bold; color: #94a3b8; margin-bottom: 4px;">Recent Food & Commute Digital Receipts:</div>
            <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.5; max-height: 110px; overflow-y: auto;" id="phone-orders-list">
                <div>🍔 <em>Swiggy Truffles Burger</em> • Aarav Sharma • ₹420 (PhonePe UPI)</div>
                <div>☕ <em>Filter Coffee Darshini</em> • Priya Patel • ₹30 (Paytm Soundbox)</div>
                <div>🛵 <em>Rapido Bike Taxi to HSR</em> • Vikram Rao • ₹85 (UPI QR)</div>
                <div>🚇 <em>Namma Metro SmartCard</em> • Sneha Kulkarni • ₹50 (Auto-debit)</div>
            </div>
            <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 5px;">
                <span>Nothing Phone 2, iPhone 15, Pixel 8</span>
                <span style="color: #10b981;">● Airtel / Jio 5G</span>
            </div>
        </div>

        <!-- CARD 3: 🐕 URBAN FAUNA & PARKS OF BENGALURU -->
        <div class="section-box" style="padding: 14px; background: #0c121e; border: 1px solid rgba(245, 158, 11, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
                <div style="font-size: 13px; font-weight: 800; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
                    <span>🐕 URBAN FAUNA & LUSH PARKS</span>
                    <span style="font-size: 10px; background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 1px 6px; border-radius: 10px;">5 DOGS • 2 CATS</span>
                </div>
                <button class="macro-btn" onclick="quickPetAnimal('d1', 'Tommy')" style="font-size: 10px; padding: 2px 8px; border-color: #fbbf24; color: #fbbf24;">🐾 Pet Tommy</button>
            </div>
            <div style="display: flex; gap: 5px; margin-bottom: 8px; overflow-x: auto; padding-bottom: 4px;">
                <button class="macro-btn" onclick="quickPetAnimal('d1', 'Tommy')" style="font-size: 9.5px; padding: 2px 6px;">🐕 Tommy (Indiranagar)</button>
                <button class="macro-btn" onclick="quickPetAnimal('d2', 'Kaalu')" style="font-size: 9.5px; padding: 2px 6px;">🐕 Kaalu (HSR)</button>
                <button class="macro-btn" onclick="quickPetAnimal('d3', 'Sheru')" style="font-size: 9.5px; padding: 2px 6px;">🐕 Sheru (Koramangala)</button>
                <button class="macro-btn" onclick="quickPetAnimal('c1', 'Mimi')" style="font-size: 9.5px; padding: 2px 6px;">🐈 Mimi (MG Rd)</button>
            </div>
            <div style="font-size: 11px; font-weight: bold; color: #94a3b8; margin-bottom: 4px;">Live Petting Encounters & Serotonin Feed:</div>
            <div style="font-size: 10.5px; color: #cbd5e1; line-height: 1.5; max-height: 100px; overflow-y: auto;" id="fauna-interactions-feed">
                <div>🐕 <em>Tommy</em> got petted by Aarav Sharma at Indiranagar 100ft Rd. Stress -20%!</div>
                <div>🐈 <em>Mimi</em> purring on Church Street cafe bench. Priya smiled.</div>
                <div>🌳 <em>Cubbon Park</em>: 8 citizens enjoying morning bamboo grove stroll.</div>
            </div>
            <div style="margin-top: 8px; font-size: 10px; color: #fbbf24; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 5px;">
                Parks: Cubbon Park (300 acres) • Lalbagh Botanical Gardens • Agara Lake
            </div>
        </div>
    </div>

    <div class="main-layout">
        <!-- Left Column: Radio, Dialogues & Newsroom -->
        <div class="section-box">
            <!-- Namma Radio 91.1 FM -->
            <div class="radio-card">
                <div class="radio-title">
                    <span>📻 NAMMA RADIO 91.1 FM — LIVE CITY BROADCAST</span>
                    <span style="font-size: 10px; color: var(--green); font-weight: normal;">● ON AIR</span>
                </div>
                <div id="radio-text" style="color: #e6edf3; font-style: italic;">Connecting to Bengaluru airwaves...</div>
            </div>

            <!-- Inter-Citizen Spoken Dialogues -->
            <div class="section-header">
                <span>INTER-CITIZEN SPOKEN DIALOGUES (Cafes, Metro & Tech Parks)</span>
                <span style="font-size: 11px; color: var(--purple);">Smallville converse.py</span>
            </div>
            <div class="feed-box" id="dialogue-feed"></div>

            <!-- The Bengaluru Chronicle Tabloid -->
            <div class="section-header" style="margin-top: 14px;">
                <span>📰 THE BENGALURU CHRONICLE NEWSROOM</span>
                <span style="font-size: 11px; color: var(--orange);" id="chronicle-vol">Vol. 1</span>
            </div>
            <div id="chronicle-headline" style="font-size: 13px; font-weight: bold; color: var(--yellow); margin-bottom: 6px;"></div>
            <div id="chronicle-story" style="font-size: 12px; color: #8b949e; margin-bottom: 10px;"></div>

            <!-- Workspace Deliverables -->
            <div class="section-header" style="margin-top: 14px;">
                <span>BENGALURU TECH DELIVERABLES (workspace/)</span>
                <span style="font-size: 11px; color: var(--cyan);">Durable Artifacts & Specs</span>
            </div>
            <div class="feed-box" id="workspace-feed"></div>

            <!-- Bengaluru Forbes Top Wealth & Wealth Multipliers -->
            <div class="section-header" style="margin-top: 14px;">
                <span>💰 BENGALURU FORBES 100 RICH LIST (Wealth Multipliers 2x, 4x, 10x+)</span>
                <span style="font-size: 11px; color: var(--yellow);">Compounded Net Worth</span>
            </div>
            <div class="feed-box" id="forbes-rich-feed" style="max-height: 160px; font-size: 11px;"></div>

            <!-- Startups & High-Tech Ventures Registry -->
            <div class="section-header" style="margin-top: 14px;">
                <span>🚀 HIGH-TECH STARTUPS & UNICORNS (Incorporated in BLR)</span>
                <span style="font-size: 11px; color: var(--cyan);">Equity & Valuations</span>
            </div>
            <div class="feed-box" id="startups-feed" style="max-height: 140px; font-size: 11px;"></div>
        </div>

        <!-- Right Column: Workplaces, Cafes, Pubs, Gyms, Parks & BMTC Transit -->
        <div class="section-box">
            <div class="section-header">
                <span>🏢 NAMMA BENGALURU PHYSICAL WORLD ENGINE</span>
                <span style="font-size: 11px; color: var(--green);" id="workplace-status">100 Live Citizens</span>
            </div>
            
            <!-- Living Fauna & Transit Fleet Status Banner -->
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 8px 10px; margin-bottom: 10px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
                <span style="color: var(--cyan); font-weight: bold;">🐾 LIVING FAUNA:</span>
                <span style="color: #f59e0b;">🐕 8 Dogs</span>
                <span style="color: #fcd34d;">🐈 6 Cats</span>
                <span style="color: #38bdf8;">🕊️ 32 Sky Birds</span>
                <span style="color: #94a3b8;">|</span>
                <span style="color: var(--purple); font-weight: bold;">🚌 TRANSIT:</span>
                <span style="color: #60a5fa;">6 BMTC Buses</span>
                <span style="color: #c084fc;">3 Metro Trains</span>
            </div>

            <!-- Quick Camera Jump Controls (10 Focused Destinations) -->
            <div style="background: #090e15; border: 1px solid var(--border); border-radius: 6px; padding: 10px; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: bold; color: var(--cyan); margin-bottom: 8px;">
                    🎥 3D CAMERA QUICK-JUMP (Offices, Pubs, Gyms, Parks & Transit):
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                    <button class="btn" style="background: linear-gradient(135deg, #0284c7, #0369a1); border: 1px solid #38bdf8; font-size: 11px; padding: 6px 8px; text-align: left; font-weight: bold; color: #fff;" onclick="if(metropolis3D) metropolis3D.cinematicWindowFlyThrough('Manyata_Tech_Park');">
                        🚀 FLY: Manyata Desks (Aarav)
                    </button>
                    <button class="btn" style="background: linear-gradient(135deg, #059669, #047857); border: 1px solid #10b981; font-size: 11px; padding: 6px 8px; text-align: left; font-weight: bold; color: #fff;" onclick="if(metropolis3D) metropolis3D.cinematicWindowFlyThrough('IISc_Research_Campus');">
                        🏫 FLY: The Academy (Ramanathan)
                    </button>
                    <button class="btn" style="background: linear-gradient(135deg, #d97706, #b45309); border: 1px solid #f59e0b; font-size: 11px; padding: 6px 8px; text-align: left; font-weight: bold; color: #fff;" onclick="if(metropolis3D) metropolis3D.cinematicWindowFlyThrough('UB_City_Luxury_Towers');">
                        💎 FLY: UB City Penthouse
                    </button>
                    <button class="btn" style="background: linear-gradient(135deg, #7c3aed, #6d28d9); border: 1px solid #c084fc; font-size: 11px; padding: 6px 8px; text-align: left; font-weight: bold; color: #fff;" onclick="if(metropolis3D) metropolis3D.cinematicWindowFlyThrough('Electronic_City_Phase_1');">
                        🖥️ FLY: E-City Silicon Hub
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Manyata_Tech_Park');">
                        🏢 Manyata Office Desks
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Church_Street_Cafes');">
                        ☕ Church St. Artisan Cafe
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Koramangala_Microbrewery_Pub');">
                        🍺 Koramangala Craft Pub
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('HSR_Cult_Fit_Gym');">
                        🏋️ HSR Cult.fit Elite Gym
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Cubbon_Park_Canopy');">
                        🌳 Cubbon Park & Fountain
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Indiranagar_100ft_Startups');">
                        🚀 Indiranagar AI Studio
                    </button>
                    <button class="btn btn-blue" style="font-size: 11px; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.flyToVenue('Gandhi_Bazaar_Heritage');">
                        ☕ Vidyarthi Bhavan Darshini
                    </button>
                    <button class="btn" style="background: rgba(30, 41, 59, 0.9); border: 1px solid #fde047; font-size: 11px; font-weight: bold; color: #fef08a; padding: 6px 8px; text-align: left;" onclick="if(metropolis3D) metropolis3D.toggleDayNight();">
                        💡 Toggle Circadian Night / Day
                    </button>
                </div>
            </div>

            <!-- Active Physical Citizen Distribution (Sum = 100) -->
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 12px; text-align: center;">
                <div style="background: #090e15; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🏫</div>
                    <div style="font-size: 11px; font-weight: bold; color: #34d399;" id="cnt-school">16</div>
                    <div style="font-size: 9px; color: #8b949e;">Class</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">💻</div>
                    <div style="font-size: 11px; font-weight: bold; color: #38bdf8;" id="cnt-desk">18</div>
                    <div style="font-size: 9px; color: #8b949e;">Desks</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">☕</div>
                    <div style="font-size: 11px; font-weight: bold; color: #fbbf24;" id="cnt-cafe">12</div>
                    <div style="font-size: 9px; color: #8b949e;">Cafes</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🍺</div>
                    <div style="font-size: 11px; font-weight: bold; color: #f59e0b;" id="cnt-pub">8</div>
                    <div style="font-size: 9px; color: #8b949e;">Pubs</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🏋️</div>
                    <div style="font-size: 11px; font-weight: bold; color: #ef4444;" id="cnt-gym">8</div>
                    <div style="font-size: 9px; color: #8b949e;">Gyms</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🌳</div>
                    <div style="font-size: 11px; font-weight: bold; color: #22c55e;" id="cnt-park">10</div>
                    <div style="font-size: 9px; color: #8b949e;">Parks</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🗣️</div>
                    <div style="font-size: 11px; font-weight: bold; color: #c084fc;" id="cnt-meeting">12</div>
                    <div style="font-size: 9px; color: #8b949e;">Huddles</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🚌</div>
                    <div style="font-size: 11px; font-weight: bold; color: #06b6d4;" id="cnt-bus">10</div>
                    <div style="font-size: 9px; color: #8b949e;">Transit</div>
                </div>
                <div style="background: #090e15; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 6px; padding: 5px 3px;">
                    <div style="font-size: 13px;">🚶</div>
                    <div style="font-size: 11px; font-weight: bold; color: #94a3b8;" id="cnt-transit">22</div>
                    <div style="font-size: 9px; color: #8b949e;">Walkers</div>
                </div>
            </div>

            <!-- Active Group Discussions & Sprint Huddles -->
            <div class="section-header" style="margin-top: 10px;">
                <span>🗣️ ACTIVE GROUP DISCUSSIONS & SPRINT HUDDLES</span>
                <span style="font-size: 11px; color: var(--purple);" id="group-conv-count">Multi-Party</span>
            </div>
            <div class="feed-box" id="group-discussions-feed" style="max-height: 160px; font-size: 11px; margin-bottom: 12px;"></div>

            <!-- Municipal City Bills & Voting -->
            <div class="section-header" style="margin-top: 14px;">
                <span>MUNICIPAL CITY COUNCIL VOTING & ORDINANCES</span>
                <span style="font-size: 11px; color: var(--green);">Vidhana Soudha Civic Engine</span>
            </div>
            <div id="bills-feed"></div>

            <!-- Minecraft / Project Sid Physical Voxel Infrastructure -->
            <div class="section-header" style="margin-top: 14px;">
                <span>🧱 VOXEL PHYSICAL INFRASTRUCTURE & CONSTRUCTION LOGS</span>
                <span style="font-size: 11px; color: #10b981;">Minecraft & Project Sid Voxel Engine</span>
            </div>
            <div id="voxel-stats-bar" style="font-size: 11px; color: #8b949e; margin-bottom: 6px; display: flex; gap: 10px;"></div>
            <div class="feed-box" id="voxel-feed" style="max-height: 120px; font-size: 11px;"></div>

            <!-- Project Sid Social Graph & P2P Bounties -->
            <div class="section-header" style="margin-top: 14px;">
                <span>💼 P2P CONTRACT MARKET & PERSISTENT SOCIAL GRAPH</span>
                <span style="font-size: 11px; color: #38bdf8;">Decentralized Barter & Bonds</span>
            </div>
            <div class="feed-box" id="p2p-feed" style="max-height: 130px; font-size: 11px;"></div>
            <!-- Families, Romance, Weddings & Lineage -->
            <div class="section-header" style="margin-top: 14px;">
                <span>💍 BENGALURU FAMILIES, WEDDINGS & GENERATIONS (Having Kids)</span>
                <span style="font-size: 11px; color: #f43f5e;">Matrimony & Lineage</span>
            </div>
            <div class="feed-box" id="families-feed" style="max-height: 140px; font-size: 11px;"></div>

            <!-- Live Life Milestones Ticker -->
            <div class="section-header" style="margin-top: 14px;">
                <span>✨ REAL-WORLD LIFE MILESTONES & ACHIEVEMENTS TICKER</span>
                <span style="font-size: 11px; color: #facc15;">Weddings, Births, Doubling & Travel</span>
            </div>
            <div class="feed-box" id="milestones-feed" style="max-height: 140px; font-size: 11px;"></div>

            <!-- Real-time Event Feed -->
            <div class="section-header" style="margin-top: 14px;">
                <span>CITY EVENT LOGS (Traffic, Transit & Economy)</span>
            </div>
            <div class="feed-box" id="event-feed" style="font-family: monospace; font-size: 11px;"></div>
        </div>
    </div>

    <!-- 100-Citizen Directory Modal -->
    <div class="modal" id="directory-modal">
        <div class="modal-content">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <h3 style="color: var(--orange);">👥 100 Autonomous Citizens of Bengaluru</h3>
                <button onclick="closeDirectoryModal()" style="background: none; border: none; color: #888; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            <div style="margin-top: 10px; display: flex; gap: 10px;">
                <input type="text" id="dir-search" class="god-input" placeholder="Search citizen by name, role, department or zone..." oninput="filterDirectory()">
            </div>
            <div class="citizen-grid" id="dir-grid"></div>
        </div>
    </div>

    <!-- Citizen Inspector Profile Modal -->
    <div class="modal" id="citizen-modal">
        <div class="modal-content" style="max-width: 480px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <h3 id="modal-name" style="color: var(--orange);">Citizen Profile</h3>
                <button onclick="closeModal()" style="background: none; border: none; color: #888; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            <div style="margin-top: 12px; font-size: 13px; line-height: 1.6;">
                <div><strong>Role:</strong> <span id="modal-role"></span></div>
                <div><strong>Department:</strong> <span id="modal-dept"></span></div>
                <div><strong>Location:</strong> <span id="modal-zone" style="color: var(--cyan);"></span></div>
                <div><strong>Bank Balance:</strong> <span id="modal-wallet" style="color: var(--green); font-weight: bold;"></span></div>
                <div><strong>Net Worth:</strong> <span id="modal-networth" style="color: #38bdf8; font-weight: bold;"></span> <span id="modal-multiplier" style="color: #facc15; font-size: 11px;"></span></div>
                <div><strong>Marital Status:</strong> <span id="modal-family" style="color: #f43f5e;"></span></div>
                <div><strong>Kids & Lineage:</strong> <span id="modal-kids" style="color: #a78bfa;"></span></div>
                <div><strong>Happiness / Joy:</strong> <span id="modal-happiness" style="color: #10b981;"></span></div>
                <div id="modal-company-box" style="display: none; color: #f59e0b; font-weight: bold; margin-top: 4px;">👑 Founder: <span id="modal-company"></span></div>
                <div><strong>Energy / Stamina:</strong> <span id="modal-energy"></span></div>
                <div style="margin-top: 8px;"><strong>Current Task:</strong></div>
                <div id="modal-action" style="background: #090e15; padding: 8px; border-radius: 4px; margin-top: 4px; font-size: 12px; color: var(--yellow);"></div>
                <div style="margin-top: 14px;">
                    <button class="btn btn-blue" id="modal-call-btn" style="width: 100%;">📞 Call Citizen Directly (Governor God Mode)</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Launch Product Campaign Modal -->
    <div class="modal" id="launch-campaign-modal">
        <div class="modal-content" style="max-width: 480px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <h3 style="color: var(--yellow);">🚀 Launch New Product Campaign</h3>
                <button onclick="closeLaunchCampaignModal()" style="background: none; border: none; color: #888; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                <div>
                    <label style="color: #94a3b8;">Product Name:</label>
                    <input type="text" id="mkt-new-name" value="Indiranagar CyberSecurity Mesh" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                </div>
                <div>
                    <label style="color: #94a3b8;">Tagline / Ad Copy:</label>
                    <input type="text" id="mkt-new-tagline" value="Zero-trust API isolation with hardware-enforced microsegmentation." style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div>
                        <label style="color: #94a3b8;">Sector:</label>
                        <select id="mkt-new-sector" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;">
                            <option value="TECH_DEV_TOOL">TECH_DEV_TOOL</option>
                            <option value="LIFESTYLE_LUXURY">LIFESTYLE_LUXURY</option>
                            <option value="BEVERAGE_FOOD">BEVERAGE_FOOD</option>
                            <option value="HEALTH_FITNESS">HEALTH_FITNESS</option>
                            <option value="FINTECH_SaaS">FINTECH_SaaS</option>
                            <option value="ECO_MOBILITY">ECO_MOBILITY</option>
                        </select>
                    </div>
                    <div>
                        <label style="color: #94a3b8;">Price (₹ INR):</label>
                        <input type="number" id="mkt-new-price" value="1999" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div>
                        <label style="color: #94a3b8;">Claimed Utility (1-10):</label>
                        <input type="number" id="mkt-new-utility" value="8.5" step="0.1" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                    </div>
                    <div>
                        <label style="color: #94a3b8;">Actual Quality (1-10):</label>
                        <input type="number" id="mkt-new-quality" value="8.8" step="0.1" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                    </div>
                </div>
                <button class="btn btn-blue" onclick="submitLaunchCampaign()" style="margin-top: 10px; padding: 8px;">🚀 Release Product into Bengaluru Metropolis</button>
            </div>
        </div>
    </div>

    <!-- A/B Split Test Modal -->
    <div class="modal" id="ab-test-modal">
        <div class="modal-content" style="max-width: 540px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 8px;">
                <h3 style="color: #8b5cf6;">⚖️ Launch Scientific A/B Market Test</h3>
                <button onclick="closeABTestModal()" style="background: none; border: none; color: #888; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                <div>
                    <label style="color: #94a3b8;">Product Base Name:</label>
                    <input type="text" id="ab-name" value="Quantum AI Code Assistant" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 6px; margin-top: 2px;" />
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <!-- Variant A -->
                    <div style="background: #090e15; border: 1px solid #0284c7; padding: 8px; border-radius: 6px;">
                        <div style="color: #38bdf8; font-weight: bold; margin-bottom: 4px;">Variant A (Benchmark-Driven)</div>
                        <label style="color: #94a3b8; font-size: 10px;">Copy / Tagline:</label>
                        <textarea id="ab-tagline-a" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px; font-size: 11px; height: 50px;">Provably deterministic AST transformations with 0% hallucinations on rust/go benchmarks.</textarea>
                        <label style="color: #94a3b8; font-size: 10px; margin-top: 4px; display: block;">Price (₹ INR):</label>
                        <input type="number" id="ab-price-a" value="1499" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px; font-size: 11px;" />
                    </div>
                    <!-- Variant B -->
                    <div style="background: #090e15; border: 1px solid #7c3aed; padding: 8px; border-radius: 6px;">
                        <div style="color: #a78bfa; font-weight: bold; margin-bottom: 4px;">Variant B (Hype / Scarcity)</div>
                        <label style="color: #94a3b8; font-size: 10px;">Copy / Tagline:</label>
                        <textarea id="ab-tagline-b" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px; font-size: 11px; height: 50px;">Supercharge your 10x coding powers! Ship products 5x faster while sipping artisan coffee.</textarea>
                        <label style="color: #94a3b8; font-size: 10px; margin-top: 4px; display: block;">Price (₹ INR):</label>
                        <input type="number" id="ab-price-b" value="2499" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid var(--border); border-radius: 4px; padding: 4px; font-size: 11px;" />
                    </div>
                </div>
                <button class="btn" onclick="submitABTest()" style="margin-top: 10px; padding: 8px; background: #8b5cf6; color: #fff;">⚖️ Deploy Concurrent A/B Split Test</button>
            </div>
        </div>
    </div>

    <!-- 4 NEW ARCHITECTURAL LAYERS: Sandbox Runtimes | Bankruptcy & Inheritance | Spatial Contagion | Generative Visual Ads -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px;">
        <!-- Card 1: Sandboxed Code Execution Runtimes -->
        <div class="section-box" style="background: linear-gradient(135deg, #090e17 0%, #0d1522 100%); border-color: rgba(56, 189, 248, 0.4);">
            <div class="section-header">
                <span style="color: var(--cyan);">⚡ SANDBOXED PYTHON EXECUTION RUNTIMES</span>
                <span style="font-size: 10px; color: var(--green);" id="sandbox-count-badge">Live Git Commits</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">Real sandboxed python executions executed by tech citizens claiming P2P market bounties:</div>
            <div id="sandbox-feed" style="display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto;"></div>
        </div>

        <!-- Card 2: Corporate Bankruptcy Court & Estate Inheritance Probate -->
        <div class="section-box" style="background: linear-gradient(135deg, #110e14 0%, #17111a 100%); border-color: rgba(248, 113, 113, 0.4);">
            <div class="section-header">
                <span style="color: #f87171;">⚖️ CORPORATE BANKRUPTCY & ESTATE PROBATE</span>
                <span style="font-size: 10px; color: #fbbf24;">Solvency Court</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">Startups liquidated when runway hits 0, plus generational asset deeds & elder retirements:</div>
            <div id="lifecycle-feed" style="display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto;"></div>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px;">
        <!-- Card 3: Spatial Word-of-Mouth Diffusion Graph -->
        <div class="section-box" style="background: linear-gradient(135deg, #0b141a 0%, #0e1d24 100%); border-color: rgba(45, 212, 191, 0.4);">
            <div class="section-header">
                <span style="color: #2dd4bf;">🌐 SPATIAL PROXIMITY WORD-OF-MOUTH CONTAGION</span>
                <span style="font-size: 10px; color: #2dd4bf;" id="diffusion-hops-badge">0 Physical Hops</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">Physical peer-to-peer transmissions occurring strictly when citizens share sectors or metro trains:</div>
            <div id="diffusion-feed" style="display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto;"></div>
        </div>

        <!-- Card 4: Generative Visual Ad Banner & Design Critique Studio -->
        <div class="section-box" style="background: linear-gradient(135deg, #16111f 0%, #1e152d 100%); border-color: rgba(168, 85, 247, 0.4);">
            <div class="section-header">
                <span style="color: #c084fc;">🎨 MULTIMODAL VISUAL AD CREATIVE & DESIGN CRITIQUE</span>
                <span style="font-size: 10px; color: #c084fc;">Certified Design Score</span>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">Visual ad banner generated for current campaign with multimodal citizen design scores:</div>
            <div id="visual-ad-container" style="border: 1px solid #334155; border-radius: 6px; overflow: hidden; max-height: 155px; margin-bottom: 6px;"></div>
            <div id="visual-ad-critique" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; font-size: 9.5px; text-align: center;"></div>
        </div>
    </div>

    <!-- CITIZEN 2-WAY SPOKEN PHONE CALL MODAL -->
    <div id="citizen-call-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); backdrop-filter: blur(6px); z-index: 9999; justify-content: center; align-items: center;">
        <div style="background: #0d1522; border: 2px solid #38bdf8; border-radius: 12px; width: 520px; max-width: 92vw; padding: 20px; box-shadow: 0 12px 40px rgba(0,0,0,0.8);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px;">
                    <span>📞 DIRECT CITIZEN 2-WAY PHONE CALL</span>
                    <span id="call-status-badge" style="font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #064e3b; color: #34d399;">LINE READY</span>
                </div>
                <button onclick="closeCitizenCallModal()" style="background: transparent; border: none; color: #94a3b8; font-size: 18px; cursor: pointer;">✕</button>
            </div>
            <div style="margin-bottom: 10px;">
                <label style="font-size: 11px; color: #94a3b8;">Select Citizen to Call:</label>
                <select id="call-citizen-select" style="width: 100%; background: #070a0f; color: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px; font-size: 12px; margin-top: 4px;">
                    <option value="Aarav Sharma">Aarav Sharma (Senior Systems Lead • Manyata)</option>
                    <option value="Priya Patel">Priya Patel (Staff Distributed Architect • Indiranagar)</option>
                    <option value="Karthik Varma">Karthik Varma (Specialty Barista & Roaster • Church St.)</option>
                    <option value="Vikram Rao">Vikram Rao (Cult.fit Athletic Trainer • HSR)</option>
                    <option value="Rajeshwari Gowda">Rajeshwari Gowda (Chief News Anchor • BLR24 TV)</option>
                </select>
            </div>
            <div style="margin-bottom: 12px;">
                <label style="font-size: 11px; color: #94a3b8;">Your Spoken Message to Citizen:</label>
                <input type="text" id="call-message-input" value="How is your current workload and wallet balance today?" style="width: 100%; background: #070a0f; color: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px; font-size: 12px; margin-top: 4px;" />
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                <button class="btn btn-blue" onclick="dialCitizenNow()" style="flex: 1; padding: 8px; font-size: 12px; font-weight: bold;">⚡ Dial & Speak Aloud</button>
                <button class="btn" onclick="hangupCall()" style="background: #ef4444; color: #fff; padding: 8px 14px; font-size: 12px;">Hang Up</button>
            </div>
            <div id="call-audio-transcript" style="background: #06090e; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; min-height: 80px; font-size: 11.5px; color: #cbd5e1; line-height: 1.5;">
                <div style="color: #64748b; font-style: italic;">Pick a citizen above and click 'Dial & Speak Aloud' to initiate an immediate 2-way synthesized voice phone call.</div>
            </div>
        </div>
    </div>

    <!-- CITIZEN SMARTPHONE INSPECTOR MODAL -->
    <div id="citizen-phone-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 9999; justify-content: center; align-items: center;">
        <div style="background: #020617; border: 2px solid #10b981; border-radius: 28px; width: 380px; max-width: 92vw; padding: 18px; box-shadow: 0 20px 50px rgba(0,0,0,0.9); position: relative;">
            <!-- Smartphone Top Speaker & Camera Punch-hole -->
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px; position: relative;">
                <div style="width: 60px; height: 4px; background: #334155; border-radius: 4px;"></div>
                <div style="width: 10px; height: 10px; background: #000; border: 1.5px solid #1e293b; border-radius: 50%; margin-left: 10px;"></div>
                <button onclick="closeCitizenPhoneModal()" style="position: absolute; right: 0; top: -6px; background: transparent; border: none; color: #94a3b8; font-size: 18px; cursor: pointer;">✕</button>
            </div>

            <!-- Citizen Selector inside Phone -->
            <div style="margin-bottom: 8px;">
                <select id="phone-citizen-select" onchange="loadCitizenPhone(this.value)" style="width: 100%; background: #0f172a; color: #fff; border: 1px solid #334155; border-radius: 8px; padding: 4px 8px; font-size: 11px;">
                    <option value="c1">Aarav Sharma (Senior Systems Lead)</option>
                </select>
            </div>

            <!-- Smartphone OS Status Bar -->
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #cbd5e1; border-bottom: 1px solid #1e293b; padding-bottom: 4px; margin-bottom: 10px;">
                <span id="phone-clock">09:15 AM</span>
                <span id="phone-carrier" style="color: #38bdf8; font-weight: bold;">Airtel 5G Plus</span>
                <span id="phone-battery" style="color: #10b981; font-weight: bold;">🔋 92%</span>
            </div>

            <!-- Handset Model Badge -->
            <div style="background: #0f172a; border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 12px; font-weight: bold; color: #fff;" id="phone-model-name">Nothing Phone (2)</div>
                    <div style="font-size: 10px; color: #94a3b8;" id="phone-os-version">Nothing OS 2.5 • Glyph Active</div>
                </div>
                <span style="font-size: 16px;">📱</span>
            </div>

            <!-- PhonePe / UPI Digital Wallet Card -->
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 12px; padding: 12px; margin-bottom: 10px; color: #fff;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 10px; font-weight: bold; letter-spacing: 0.5px; opacity: 0.9;">PHONEPE / BHIM UPI</span>
                    <span style="font-size: 9px; background: rgba(255,255,255,0.25); padding: 2px 6px; border-radius: 4px;">FAST-PAY</span>
                </div>
                <div style="font-size: 18px; font-weight: 900;" id="phone-upi-balance">₹24,580.00</div>
                <div style="font-size: 9.5px; opacity: 0.85; margin-top: 2px;" id="phone-upi-id">aarav.sharma@oksbi</div>
            </div>

            <!-- WhatsApp / Signal Active Chat Threads -->
            <div style="margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: bold; color: #38bdf8; margin-bottom: 5px; display: flex; justify-content: space-between;">
                    <span>💬 WHATSAPP & SIGNAL THREADS</span>
                    <span style="font-size: 9px; color: #10b981;">● End-to-End Encrypted</span>
                </div>
                <div id="phone-chat-threads" style="background: #0b1320; border: 1px solid #1e293b; border-radius: 8px; padding: 8px; max-height: 120px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; font-size: 10px;"></div>
            </div>

            <!-- Swiggy & Rapido Digital Receipts -->
            <div>
                <div style="font-size: 11px; font-weight: bold; color: #f59e0b; margin-bottom: 5px;">
                    🛵 RECENT SWIGGY & RAPIDO TRANSACTIONS
                </div>
                <div id="phone-transactions-list" style="background: #0b1320; border: 1px solid #1e293b; border-radius: 8px; padding: 8px; max-height: 95px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; font-size: 10px;"></div>
            </div>
        </div>
    </div>

    <!-- CITIZEN DEDICATED HOUSING & LEASE MODAL -->
    <div id="citizen-housing-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 9999; justify-content: center; align-items: center;">
        <div style="background: #0d1522; border: 2px solid #38bdf8; border-radius: 14px; width: 480px; max-width: 92vw; padding: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.9);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px;">
                    <span>🏡 CITIZEN RESIDENCE & LEASE AGREEMENT</span>
                    <span id="house-occupancy-badge" style="font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #064e3b; color: #34d399;">HOME</span>
                </div>
                <button onclick="closeCitizenHousingModal()" style="background: transparent; border: none; color: #94a3b8; font-size: 18px; cursor: pointer;">✕</button>
            </div>

            <!-- Citizen Selector inside Housing -->
            <div style="margin-bottom: 12px;">
                <label style="font-size: 11px; color: #94a3b8;">Select Citizen Tenant / Owner:</label>
                <select id="housing-citizen-select" onchange="loadCitizenHousing(this.value)" style="width: 100%; background: #070a0f; color: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px; font-size: 12px; margin-top: 4px;">
                    <option value="c1">Aarav Sharma</option>
                </select>
            </div>

            <!-- Housing Property Details Card -->
            <div style="background: #06090e; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 13px; font-weight: bold; color: #fff; margin-bottom: 4px;" id="house-complex-name">Dev Co-Living PG</div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;" id="house-address">Flat 302, Indiranagar 100ft Road, Bengaluru</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
                    <div style="background: #0d1726; padding: 6px 8px; border-radius: 6px;">
                        <span style="color: #94a3b8;">Monthly Rent:</span><br>
                        <strong style="color: #10b981;" id="house-monthly-rent">₹14,500 / month</strong>
                    </div>
                    <div style="background: #0d1726; padding: 6px 8px; border-radius: 6px;">
                        <span style="color: #94a3b8;">Lease Status:</span><br>
                        <strong style="color: #38bdf8;" id="house-lease-type">Registered Lease (Tenant)</strong>
                    </div>
                </div>
            </div>

            <!-- Room Furnishings & Amenities -->
            <div>
                <div style="font-size: 11px; font-weight: bold; color: #38bdf8; margin-bottom: 6px;">🛋️ ROOM FURNISHINGS & AMENITIES:</div>
                <div id="house-furnishings-list" style="background: #070a0f; border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #cbd5e1; display: flex; flex-direction: column; gap: 4px;">
                    <div>• Ergonomic Standing Desk (Dual Monitors)</div>
                    <div>• Orthopedic Memory Foam Bed</div>
                    <div>• Traditional South Indian Filter Coffee French Press</div>
                    <div>• High-Speed 1 Gbps Fiber Connection</div>
                    <div>• Monsoon Umbrella & Bangalore Winter Jacket Stand</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('bengaluru-canvas');
        const ctx = canvas.getContext('2d');
        let worldData = null;
        let isAutoRunning = true;
        let trainOffsets = [0, 0.33, 0.66];
        let citizenDots = [];
        let activeViewMode = '3d';
        let metropolis3D = null;

        window.addEventListener('DOMContentLoaded', () => {
            try {
                if (window.VoxelMetropolis3D) {
                    metropolis3D = new VoxelMetropolis3D('threejs-container');
                    window.metropolis3D = metropolis3D;
                    window.voxelEngine = metropolis3D;
                }
            } catch (e) {
                console.warn("3D engine load note:", e);
            }
        });

        function switchViewMode(mode) {
            activeViewMode = mode;
            const btn3d = document.getElementById('btn-view-3d');
            const btn2d = document.getElementById('btn-view-2d');
            const threeDiv = document.getElementById('threejs-container');
            const canvas2d = document.getElementById('bengaluru-canvas');
            const hint3d = document.getElementById('controls-hint-3d');

            if (mode === '3d') {
                btn3d.className = 'btn btn-blue';
                btn3d.style.background = '';
                btn3d.style.color = '';
                btn2d.className = 'btn';
                btn2d.style.background = '#1e293b';
                btn2d.style.color = '#94a3b8';
                threeDiv.style.display = 'block';
                canvas2d.style.display = 'none';
                if (hint3d) hint3d.style.display = 'flex';
                if (metropolis3D) metropolis3D.onWindowResize();
            } else {
                btn2d.className = 'btn btn-blue';
                btn2d.style.background = '';
                btn2d.style.color = '';
                btn3d.className = 'btn';
                btn3d.style.background = '#1e293b';
                btn3d.style.color = '#94a3b8';
                threeDiv.style.display = 'none';
                canvas2d.style.display = 'block';
                if (hint3d) hint3d.style.display = 'none';
                resizeCanvas();
            }
        }

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
            drawMap();
        }
        window.addEventListener('resize', resizeCanvas);

        // Moving Metro Trains Animation Loop (runs only when 2D Strategic Radar is active)
        function animateTrains() {
            if (activeViewMode === '2d') {
                trainOffsets = trainOffsets.map(o => (o + 0.003) % 1.0);
                drawMap();
            }
            requestAnimationFrame(animateTrains);
        }

        function drawTrack(linePoints, color, sx, sy, width, label) {
            if (!linePoints || linePoints.length < 2) return;
            ctx.beginPath();
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.setLineDash([8, 6]);
            ctx.moveTo(linePoints[0].x * sx, linePoints[0].y * sy);
            for (let i = 1; i < linePoints.length; i++) {
                ctx.lineTo(linePoints[i].x * sx, linePoints[i].y * sy);
            }
            ctx.stroke();
            ctx.setLineDash([]);
        }

        function getPointOnPolyline(points, t, sx, sy) {
            if (points.length < 2) return {x: 0, y: 0};
            const segCount = points.length - 1;
            const segIndex = Math.min(Math.floor(t * segCount), segCount - 1);
            const segT = (t * segCount) - segIndex;
            const p1 = points[segIndex];
            const p2 = points[segIndex + 1];
            return {
                x: (p1.x + (p2.x - p1.x) * segT) * sx,
                y: (p1.y + (p2.y - p1.y) * segT) * sy
            };
        }

        function drawMap() {
            if (!canvas.width || !worldData) return;
            const w = canvas.width;
            const h = canvas.height;
            const sx = w / 1000;
            const sy = h / 750;

            ctx.clearRect(0, 0, w, h);

            // 1. Draw Namma Metro Lines
            if (worldData.metro_lines) {
                // Purple Line
                drawTrack(worldData.metro_lines[0], '#bc8cff', sx, sy, 3, 'Purple Line');
                // Green Line
                drawTrack(worldData.metro_lines[1], '#3fb950', sx, sy, 3, 'Green Line');
                // Blue Line
                drawTrack(worldData.metro_lines[2], '#58a6ff', sx, sy, 3, 'Airport Blue Line');

                // Moving Trains
                worldData.metro_lines.forEach((line, idx) => {
                    const trainPos = getPointOnPolyline(line, trainOffsets[idx], sx, sy);
                    ctx.beginPath();
                    ctx.arc(trainPos.x, trainPos.y, 6, 0, Math.PI * 2);
                    ctx.fillStyle = '#fff';
                    ctx.shadowColor = '#bc8cff';
                    ctx.shadowBlur = 10;
                    ctx.fill();
                    ctx.shadowBlur = 0;
                });
            }

            // 2. Draw 16 Bengaluru Hubs
            const coords = worldData.zone_coordinates;
            for (const [zId, z] of Object.entries(coords)) {
                const zx = z.x * sx;
                const zy = z.y * sy;
                const zw = z.w * sx;
                const zh = z.h * sy;

                // Hub Background
                ctx.fillStyle = z.color + '18';
                ctx.fillRect(zx, zy, zw, zh);

                // Hub Border
                ctx.strokeStyle = z.color + '88';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(zx, zy, zw, zh);

                // Zone Title & Category
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 11px monospace';
                ctx.fillText(z.name, zx + 8, zy + 18);

                const meta = (worldData.zone_metadata && worldData.zone_metadata[zId]) || {};
                if (meta.category) {
                    ctx.fillStyle = z.color;
                    ctx.font = '9px monospace';
                    ctx.fillText(meta.category.toUpperCase(), zx + 8, zy + 32);
                }
            }

            // 3. Draw 100 Active Citizens
            if (worldData.persona_states) {
                const zoneBuckets = {};
                worldData.persona_states.forEach(p => {
                    if (!zoneBuckets[p.zone]) zoneBuckets[p.zone] = [];
                    zoneBuckets[p.zone].push(p);
                });

                for (const [zId, occupants] of Object.entries(zoneBuckets)) {
                    const z = coords[zId];
                    if (!z) continue;
                    const zx = z.x * sx;
                    const zy = z.y * sy;
                    const zw = z.w * sx;
                    const zh = z.h * sy;

                    occupants.forEach((p, idx) => {
                        const cols = 7;
                        const col = idx % cols;
                        const row = Math.floor(idx / cols);
                        const px = zx + 12 + col * ((zw - 24) / (cols - 1 || 1));
                        const py = zy + 42 + row * 10;

                        ctx.beginPath();
                        ctx.arc(px, py, 3.5, 0, Math.PI * 2);
                        ctx.fillStyle = p.energy < 40 ? '#f85149' : (p.wallet_inr > 35000 ? '#e3b341' : '#3fb950');
                        ctx.fill();

                        // Save dot for click inspector
                        citizenDots.push({ x: px, y: py, radius: 4, persona: p });
                    });
                }
            }

            // 4. Draw Active Spoken Dialogue Bubbles
            if (worldData.active_conversations) {
                worldData.active_conversations.forEach(c => {
                    const z = coords[c.zone];
                    if (!z) return;
                    const zx = z.x * sx;
                    const zy = z.y * sy;

                    ctx.fillStyle = 'rgba(16, 22, 32, 0.9)';
                    ctx.strokeStyle = '#bc8cff';
                    ctx.lineWidth = 1;
                    const bubbleW = 160 * sx;
                    const bubbleH = 34 * sy;
                    ctx.fillRect(zx + 5, zy - 38 * sy, bubbleW, bubbleH);
                    ctx.strokeRect(zx + 5, zy - 38 * sy, bubbleW, bubbleH);

                    ctx.fillStyle = '#bc8cff';
                    ctx.font = 'bold 9px monospace';
                    ctx.fillText('💬 ' + c.speaker_1 + ' & ' + c.speaker_2, zx + 8, zy - 24 * sy);
                    ctx.fillStyle = '#c9d1d9';
                    ctx.font = '8px monospace';
                    ctx.fillText(c.turn_1.substring(0, 26) + '...', zx + 8, zy - 12 * sy);
                });
            }
        }

        // ── RENDER HELPERS (called by SSE + fast polls) ──────────────────
        function renderDialogues(convList) {
            if (!convList || !convList.length) return;
            const dFeed = document.getElementById('dialogue-feed');
            if (dFeed) {
                dFeed.innerHTML = convList.slice(0, 8).map(c => `
                    <div class="dialogue-item">
                        <div class="dialogue-meta">📍 ${c.zone.replace(/_/g,' ')} ${c.venue ? '• ' + c.venue : ''} • ${c.world_time || ''} (Affinity: ${c.affinity || '0.85'})</div>
                        <div class="dialogue-turn"><span class="speaker-name">${c.speaker_1}:</span> "${c.turn_1}"</div>
                        <div class="dialogue-turn"><span class="speaker-name">${c.speaker_2}:</span> "${c.turn_2}"</div>
                    </div>
                `).join('');
            }
            const gFeed = document.getElementById('group-discussions-feed');
            if (gFeed) {
                const groupConvs = convList.filter(c => c.is_group);
                const listToRender = groupConvs.length ? groupConvs : convList.slice(0, 4);
                gFeed.innerHTML = listToRender.map(c => `
                    <div style="background:#0b131e;border-left:3px solid var(--purple);padding:8px 10px;border-radius:0 6px 6px 0;margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--text-muted);margin-bottom:3px;">
                            <span>🏢 ${c.venue || c.zone.replace(/_/g,' ')}</span>
                            <span style="color:var(--cyan);font-weight:bold;">${c.world_time || ''}</span>
                        </div>
                        <div style="font-weight:bold;color:var(--yellow);font-size:11px;margin-bottom:4px;">🎯 ${c.topic || 'Engineering Architecture Sync'}</div>
                        <div style="font-size:11px;color:#cbd5e1;line-height:1.4;">
                            <div><span style="color:var(--cyan);font-weight:600;">${c.speaker_1}:</span> "${c.turn_1}"</div>
                            <div style="margin-top:2px;"><span style="color:var(--green);font-weight:600;">${c.speaker_2}:</span> "${c.turn_2}"</div>
                            ${c.turn_3 ? `<div style="margin-top:2px;"><span style="color:var(--purple);font-weight:600;">${c.speaker_3}:</span> "${c.turn_3}"</div>` : ''}
                            ${c.turn_4 ? `<div style="margin-top:2px;"><span style="color:var(--orange);font-weight:600;">${c.speaker_4}:</span> "${c.turn_4}"</div>` : ''}
                        </div>
                    </div>
                `).join('');
                const gCount = document.getElementById('group-conv-count');
                if (gCount) gCount.innerText = (groupConvs.length || listToRender.length) + ' Active Huddles';
            }
            const mConvs = document.getElementById('m-convs');
            if (mConvs) mConvs.innerText = convList.length + ' Dialogues';
        }

        function renderEvents(evtList) {
            if (!evtList || !evtList.length) return;
            const eFeed = document.getElementById('event-feed');
            eFeed.innerHTML = evtList.slice(0, 12).map(e => `
                <div style="padding:4px 0;border-bottom:1px solid #16202c;">
                    <span style="color:#8b949e;">[${e.time}]</span>
                    <span style="color:var(--cyan);">${e.name}</span>
                    (${e.zone.replace(/_/g,' ')}): ${e.action}
                </div>
            `).join('');
        }

        // applyTickData — handles a full telemetry snapshot (from SSE or fetchState)
        function applyTickData(data) {
            if (!data) return;
            if (!data.citizens && data.persona_states) data.citizens = data.persona_states;
            worldData = data;
            citizenDots = [];

            document.getElementById('world-clock').innerText = data.world_time;

            // Circadian Phase Badge Sync
            if (data.circadian_phase) {
                const badge = document.getElementById('circadian-badge');
                const icon = document.getElementById('circadian-icon');
                const text = document.getElementById('circadian-text');
                const cat = data.circadian_phase_category || 'MORNING';
                if (text) text.innerText = data.circadian_phase;
                if (icon && badge) {
                    if (cat === 'MIDNIGHT') { icon.innerText = '🌙'; badge.style.borderColor = '#818cf8'; badge.style.color = '#c7d2fe'; badge.style.background = 'rgba(99, 102, 241, 0.2)'; }
                    else if (cat === 'EARLY_MORNING') { icon.innerText = '🌅'; badge.style.borderColor = '#f59e0b'; badge.style.color = '#fde68a'; badge.style.background = 'rgba(245, 158, 11, 0.2)'; }
                    else if (cat === 'MORNING') { icon.innerText = '☀️'; badge.style.borderColor = '#38bdf8'; badge.style.color = '#bae6fd'; badge.style.background = 'rgba(56, 189, 248, 0.2)'; }
                    else if (cat === 'AFTERNOON') { icon.innerText = '🥪'; badge.style.borderColor = '#fbbf24'; badge.style.color = '#fef08a'; badge.style.background = 'rgba(251, 191, 36, 0.2)'; }
                    else if (cat === 'LATE_AFTERNOON') { icon.innerText = '🌧️'; badge.style.borderColor = '#fb923c'; badge.style.color = '#fed7aa'; badge.style.background = 'rgba(251, 146, 60, 0.2)'; }
                    else if (cat === 'EVENING') { icon.innerText = '🌆'; badge.style.borderColor = '#c084fc'; badge.style.color = '#e9d5ff'; badge.style.background = 'rgba(192, 132, 252, 0.2)'; }
                    else { icon.innerText = '🍺'; badge.style.borderColor = '#60a5fa'; badge.style.color = '#bfdbfe'; badge.style.background = 'rgba(96, 165, 250, 0.2)'; }
                }
            }

            document.getElementById('m-count').innerText = data.total_citizens + ' Active';
            if (data.economy) {
                const gdpStr = data.economy.real_gdp_crores || data.economy.total_gdp_inr;
                const gdpGrowth = data.economy.annual_growth_rate ? ` (${data.economy.annual_growth_rate})` : '';
                document.getElementById('m-gdp').innerText = gdpStr + gdpGrowth;
            }
            document.getElementById('m-index').innerText = data.blr_tech_index;
            document.getElementById('m-silk').innerText = data.silk_board_congestion + '% Gridlock';
            document.getElementById('m-energy').innerText = data.economy.mean_energy;

            if (data.weather) {
                const aqiStr = data.weather.aqi ? ` • AQI ${data.weather.aqi}` : '';
                document.getElementById('b-weather').innerText = data.weather.temp + ' • ' + data.weather.condition + aqiStr;
            }

            if (metropolis3D) {
                if (typeof data.time_fraction === 'number') {
                    metropolis3D.syncWorldTime(data.time_fraction, data.circadian_phase_category);
                }
                if (data.weather) {
                    metropolis3D.setWeather(data.weather.condition);
                }
            }
            if (data.stocks) {
                document.getElementById('stock-items').innerHTML = data.stocks.map(s => {
                    const isUp = s.change.startsWith('+');
                    return `<div class="stock-item">
                        <span class="stock-sym">${s.symbol}</span>
                        <span class="stock-val">₹${s.price}</span>
                        <span class="${isUp ? 'stock-up' : 'stock-down'}">${s.change}</span>
                    </div>`;
                }).join('');
            }
            if (data.radio_broadcasts && data.radio_broadcasts.length > 0) {
                document.getElementById('radio-text').innerText = data.radio_broadcasts[0].message;
            }
            if (data.chronicle_headlines && data.chronicle_headlines.length > 0) {
                const top = data.chronicle_headlines[0];
                document.getElementById('chronicle-vol').innerText = top.edition;
                document.getElementById('chronicle-headline').innerText = '⚡ ' + top.headline;
                document.getElementById('chronicle-story').innerText = top.lead_story;
            }
            if (data.recent_conversations) renderDialogues(data.recent_conversations);
            if (data.recent_events) renderEvents(data.recent_events);

            // Housing & Leases Telemetry
            if (data.housing_state) {
                const atHome = document.getElementById('house-at-home');
                const sleeping = document.getElementById('house-sleeping');
                const rent = document.getElementById('house-rent');
                if (atHome) atHome.innerText = data.housing_state.citizens_at_home;
                if (sleeping) sleeping.innerText = data.housing_state.citizens_sleeping;
                if (rent) rent.innerText = data.housing_state.total_rent_collected_inr;
            }

            // Phones & UPI Telemetry
            if (data.phones_state) {
                const count = document.getElementById('phone-count');
                const upiVol = document.getElementById('phone-upi-vol');
                if (count) count.innerText = data.phones_state.total_phones + ' / 100';
                if (upiVol) upiVol.innerText = data.phones_state.total_upi_volume_inr;
                if (data.phones_state.active_orders && data.phones_state.active_orders.length > 0) {
                    const pList = document.getElementById('phone-orders-list');
                    if (pList) {
                        pList.innerHTML = data.phones_state.active_orders.slice(-4).reverse().map(o => `
                            <div>🛵 <em>${o.vendor}</em> • ${o.citizen} • ₹${o.price_inr} (${o.payment_method})</div>
                        `).join('');
                    }
                }
            }

            // Fauna Telemetry
            if (data.fauna_state && data.fauna_state.recent_petting_moments && data.fauna_state.recent_petting_moments.length > 0) {
                const fFeed = document.getElementById('fauna-interactions-feed');
                if (fFeed) {
                    fFeed.innerHTML = data.fauna_state.recent_petting_moments.slice(-4).reverse().map(m => `
                        <div>🐕 <em>${m.dog_name || 'Sheru'}</em>: ${m.message}</div>
                    `).join('');
                }
            }

            if (data.city_bills) {
                document.getElementById('bills-feed').innerHTML = data.city_bills.map(b => `
                    <div class="bill-card">
                        <div class="bill-title">
                            <span>${b.title}</span>
                            <span class="bill-status ${b.status === 'PASSED' ? 'status-passed' : 'status-voting'}">${b.status}</span>
                        </div>
                        <div style="font-size:11px;color:var(--text-muted);margin-top:3px;">${b.desc}</div>
                        <div style="font-size:11px;margin-top:4px;color:var(--cyan);">Votes: 👍 ${b.yes_votes} | 👎 ${b.no_votes}</div>
                    </div>
                `).join('');
            }
            if (data.voxel_world) {
                const blockCount = data.voxel_world.total_constructed_blocks || 0;
                document.getElementById('m-blocks').innerText = blockCount + ' Blocks';
                document.getElementById('voxel-stats-bar').innerHTML =
                    `<span><strong>Total:</strong> ${blockCount} Blocks</span>
                     <span><strong>Zones:</strong> ${data.voxel_world.active_construction_zones || 0}</span>
                     <span><strong>Builders:</strong> ${data.voxel_world.active_citizen_builders || 0}</span>`;
                if (data.voxel_world.recent_construction_logs) {
                    document.getElementById('voxel-feed').innerHTML = data.voxel_world.recent_construction_logs.slice(0, 6).map(l => `
                        <div style="padding:3px 0;border-bottom:1px solid #16202c;">
                            <span style="color:#10b981;">[Tick #${l.tick}]</span> <strong>${l.builder}</strong> in <em>${l.zone.replace(/_/g,' ')}</em>: ${l.details} ${l.coords}
                        </div>
                    `).join('');
                }
            }
            if (data.p2p_bounties) {
                document.getElementById('m-bounties').innerText = data.p2p_bounties.length + ' Open';
                let p2pHTML = '<div style="font-weight:bold;color:var(--orange);margin-bottom:3px;">🎯 Open Bounties:</div>';
                p2pHTML += data.p2p_bounties.slice(0, 3).map(b => `
                    <div style="padding:2px 0;color:#e6edf3;">• <strong>${b.title}</strong> — <span style="color:var(--green);">₹${b.reward_inr}</span> [${b.zone.replace(/_/g,' ')}] (by ${b.creator})</div>
                `).join('');
                if (data.social_bonds && data.social_bonds.length > 0) {
                    p2pHTML += '<div style="font-weight:bold;color:var(--purple);margin:6px 0 2px;">🤝 Persistent Social Bonds:</div>';
                    p2pHTML += data.social_bonds.slice(0, 3).map(s => `
                        <div style="padding:2px 0;color:#8b949e;">• ${s.citizen_a} ↔ ${s.citizen_b}: <span style="color:var(--cyan);">${s.status.toUpperCase()}</span> (Trust: ${s.trust}, Interactions: ${s.interactions})</div>
                    `).join('');
                }
                const p2pEl = document.getElementById('p2p-feed');
                if (p2pEl) p2pEl.innerHTML = p2pHTML;
            }

            if (data.tv_broadcast) renderLiveTV(data.tv_broadcast);
            if (data.social_pulse) renderSocialPulse(data.social_pulse);
            if (data.real_intel) renderRealIntel(data.real_intel);

            const select = document.getElementById('god-target');
            if (select.children.length === 1 && data.persona_states) {
                data.persona_states.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.innerText = `${p.name} (${p.role} @ ${p.zone.replace(/_/g,' ')})`;
                    select.appendChild(opt);
                });
            }
            if (metropolis3D && data.persona_states) {
                metropolis3D.updateCitizens(data.persona_states);
                if (data.weather) metropolis3D.setWeather(data.weather);
            }
            if (data.persona_states) {
                let dCnt = 0, cCnt = 0, pCnt = 0, gCnt = 0, pkCnt = 0, mCnt = 0, bCnt = 0, tCnt = 0;
                data.persona_states.forEach(p => {
                    const act = p.activity_state || '';
                    if (act === 'OFFICE_WORK') dCnt++;
                    else if (act === 'CAFE_HANGOUT' || act === 'DARSHINI_VISIT') cCnt++;
                    else if (act === 'PUB_PARTY') pCnt++;
                    else if (act === 'GYM_WORKOUT') gCnt++;
                    else if (act === 'PARK_STROLL') pkCnt++;
                    else if (act === 'CONFERENCE_MEETING' || act === 'GROUP_DISCUSSION') mCnt++;
                    else if (act === 'BUS_COMMUTE' || act === 'METRO_COMMUTE') bCnt++;
                    else tCnt++;
                });
                const dEl = document.getElementById('cnt-desk'); if (dEl) dEl.innerText = dCnt;
                const cEl = document.getElementById('cnt-cafe'); if (cEl) cEl.innerText = cCnt;
                const pEl = document.getElementById('cnt-pub'); if (pEl) pEl.innerText = pCnt;
                const gEl = document.getElementById('cnt-gym'); if (gEl) gEl.innerText = gCnt;
                const pkEl = document.getElementById('cnt-park'); if (pkEl) pkEl.innerText = pkCnt;
                const mEl = document.getElementById('cnt-meeting'); if (mEl) mEl.innerText = mCnt;
                const bEl = document.getElementById('cnt-bus'); if (bEl) bEl.innerText = bCnt;
                const tEl = document.getElementById('cnt-transit'); if (tEl) tEl.innerText = tCnt;
            }

            // Real Macro-GDP & National Accounting Engine HUD
            if (data.macro_gdp) {
                const mg = data.macro_gdp;
                const gH = document.getElementById('gdp-headline');
                if (gH) gH.innerText = `₹${mg.gdp_crores.toLocaleString()} Cr (+${mg.annual_growth_rate}% YoY)`;
                const gc = document.getElementById('gdp-c'); if (gc) gc.innerText = `₹${mg.consumption_c_cr.toLocaleString()} Cr`;
                const gi = document.getElementById('gdp-i'); if (gi) gi.innerText = `₹${mg.investment_i_cr.toLocaleString()} Cr`;
                const gg = document.getElementById('gdp-g'); if (gg) gg.innerText = `₹${mg.govt_spending_g_cr.toLocaleString()} Cr`;
                const gnx = document.getElementById('gdp-nx'); if (gnx) gnx.innerText = `₹${mg.net_exports_nx_cr.toLocaleString()} Cr`;
                const gt = document.getElementById('gdp-treasury'); if (gt) gt.innerText = `₹${(mg.city_treasury_inr / 10000000).toFixed(2)} Cr`;
            }

            // Bengaluru Forbes 100 Rich List & Wealth Multipliers
            if (data.forbes_rich_list) {
                const fFeed = document.getElementById('forbes-rich-feed');
                if (fFeed) {
                    fFeed.innerHTML = data.forbes_rich_list.slice(0, 5).map((r, i) => `
                        <div style="padding: 4px 0; border-bottom: 1px solid #16202c; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: var(--yellow); font-weight: bold;">#${i+1}</span>
                                <strong style="color: #fff;">${r.name}</strong>
                                <span style="color: var(--text-muted); font-size: 10px;">(${r.role.slice(0, 22)})</span>
                                ${r.company ? `<div style="font-size: 10px; color: #f59e0b;">👑 Founder: ${r.company}</div>` : ''}
                            </div>
                            <div style="text-align: right;">
                                <div style="color: var(--green); font-weight: bold;">₹${r.net_worth_inr.toLocaleString()}</div>
                                <div style="font-size: 10px; color: var(--cyan);">${r.multiplier} Multiplier</div>
                            </div>
                        </div>
                    `).join('');
                }
            }

            // High-Tech Startups & Unicorns Registry
            if (data.active_startups) {
                const sFeed = document.getElementById('startups-feed');
                if (sFeed) {
                    sFeed.innerHTML = data.active_startups.slice(0, 4).map(s => `
                        <div style="padding: 4px 0; border-bottom: 1px solid #16202c;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #38bdf8;">🚀 ${s.name}</strong>
                                <span style="color: var(--green); font-weight: bold;">₹${(s.valuation_inr / 100000).toFixed(1)}L Val</span>
                            </div>
                            <div style="font-size: 10px; color: #8b949e;">Founder: ${s.founder_name} • Sector: ${s.sector}</div>
                        </div>
                    `).join('');
                }
            }

            // Families, Weddings & Generations
            if (data.active_families) {
                const famFeed = document.getElementById('families-feed');
                if (famFeed) {
                    famFeed.innerHTML = data.active_families.slice(0, 4).map(f => `
                        <div style="padding: 4px 0; border-bottom: 1px solid #16202c;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong style="color: #f43f5e;">💍 ${f.couple}</strong>
                                <span style="color: #a78bfa; font-weight: bold;">${f.happiness} Joy</span>
                            </div>
                            <div style="font-size: 10px; color: #8b949e;">
                                ${f.kids_count > 0 ? `🍼 ${f.kids_count} Children: ${f.kids.join(', ')}` : 'Newlyweds • Planning family'}
                            </div>
                        </div>
                    `).join('');
                }
            }

            // Real-World Life Milestones Ticker
            if (data.life_milestones) {
                const mFeed = document.getElementById('milestones-feed');
                if (mFeed) {
                    mFeed.innerHTML = data.life_milestones.slice(0, 5).map(m => `
                        <div style="padding: 4px 0; border-bottom: 1px solid #16202c;">
                            <div>
                                <span>${m.icon || '✨'}</span>
                                <strong style="color: #facc15;">[Tick #${m.tick}]</strong>
                                <span style="color: #e6edf3; font-weight: bold;">${m.title}</span>
                            </div>
                            <div style="font-size: 10px; color: #8b949e; margin-left: 18px;">${m.desc}</div>
                        </div>
                    `).join('');
                }
            }

            // Synthetic Focus Group & Marketing Intelligence Telemetry
            if (data.marketing_intelligence && data.marketing_intelligence.analytics) {
                renderMarketingStudio(data.marketing_intelligence.analytics);
            }

            // 4 New Simulation Layers
            if (data.sandbox_executions) renderSandboxRuns(data.sandbox_executions);
            if (data.lifecycle_stats) renderLifecycleStats(data.lifecycle_stats);
            if (data.spatial_diffusion) renderSpatialDiffusion(data.spatial_diffusion);
            if (data.radio_broadcasts && data.radio_broadcasts.length > 0 && typeof speakRadioBroadcast === 'function') {
                speakRadioBroadcast(data.radio_broadcasts[0]);
            }

            if (activeViewMode === '2d') drawMap();
        }

        let VOICE_ENABLED = true;
        let lastSpokenRadio = "";

        function toggleVoice() {
            VOICE_ENABLED = !VOICE_ENABLED;
            const btn = document.getElementById('voice-toggle-btn');
            if (btn) {
                btn.innerText = VOICE_ENABLED ? '🔊 Voice: ON' : '🔇 Voice: OFF';
                btn.style.borderColor = VOICE_ENABLED ? '#38bdf8' : '#64748b';
                btn.style.color = VOICE_ENABLED ? '#38bdf8' : '#94a3b8';
            }
            if (!VOICE_ENABLED && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        }

        function speakRadioBroadcast(broadcast) {
            if (!VOICE_ENABLED || !('speechSynthesis' in window) || !broadcast) return;
            if (broadcast.message === lastSpokenRadio) return;
            lastSpokenRadio = broadcast.message;
            const u = new SpeechSynthesisUtterance(broadcast.message);
            u.rate = 1.05;
            u.pitch = 1.12;
            window.speechSynthesis.speak(u);
        }

        function renderSandboxRuns(runs) {
            const feed = document.getElementById('sandbox-feed');
            const badge = document.getElementById('sandbox-count-badge');
            if (!feed || !runs) return;
            if (badge) badge.innerText = `${runs.length} Commits Tracked`;
            if (runs.length === 0) {
                feed.innerHTML = '<div style="color: #64748b; font-size: 11px;">Awaiting next P2P bounty execution...</div>';
                return;
            }
            feed.innerHTML = runs.slice().reverse().map(r => `
                <div style="background: #06090e; border: 1px solid ${r.status === 'PASSED' ? '#10b981' : '#ef4444'}; border-radius: 6px; padding: 6px 8px; font-size: 10.5px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                        <strong style="color: #38bdf8;">${r.title}</strong>
                        <span style="font-size: 9px; padding: 1px 5px; border-radius: 4px; background: ${r.status === 'PASSED' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}; color: ${r.status === 'PASSED' ? '#34d399' : '#f87171'}; font-weight: bold;">${r.status} (${r.elapsed_ms}ms)</span>
                    </div>
                    <div style="color: #94a3b8; font-size: 10px;">Dev: <span style="color: #fff;">${r.citizen_name}</span> | <span style="color: #a78bfa;">${r.git_commit}</span> | 🕒 ${r.timestamp}</div>
                    ${r.stdout ? `<div style="background: #030712; padding: 3px 6px; border-radius: 4px; margin-top: 3px; font-family: monospace; color: #a5f3fc; font-size: 9.5px;">${r.stdout}</div>` : ''}
                </div>
            `).join('');
        }

        function renderLifecycleStats(stats) {
            const feed = document.getElementById('lifecycle-feed');
            if (!feed || !stats) return;
            const liqs = stats.recent_liquidations || [];
            const inh = stats.recent_inheritances || [];
            if (liqs.length === 0 && inh.length === 0) {
                feed.innerHTML = '<div style="color: #64748b; font-size: 11px;">Metropolis solvency healthy. Startups maintaining positive runway buffers.</div>';
                return;
            }
            let html = '';
            liqs.forEach(l => {
                html += `
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 6px; padding: 6px 8px; font-size: 10px; color: #fca5a5; margin-bottom: 4px;">
                        <strong>🚨 LIQUIDATION:</strong> ${l.company} (${l.sector}) ran out of capital. Founder: ${l.founder} laid off. Desks auctioned in Manyata.
                    </div>
                `;
            });
            inh.forEach(i => {
                html += `
                    <div style="background: rgba(251, 191, 36, 0.1); border: 1px solid #fbbf24; border-radius: 6px; padding: 6px 8px; font-size: 10px; color: #fde68a; margin-bottom: 4px;">
                        <strong>📜 ESTATE DEED:</strong> ${i.grantor} transferred ${i.amount_inr} generational assets to apprentice heir ${i.heir}.
                    </div>
                `;
            });
            feed.innerHTML = html;
        }

        function renderSpatialDiffusion(diffusion) {
            const feed = document.getElementById('diffusion-feed');
            const badge = document.getElementById('diffusion-hops-badge');
            if (!feed || !diffusion) return;
            if (badge) badge.innerText = `${diffusion.total_spatial_hops || 0} Physical Hops`;
            const txs = diffusion.recent_transmissions || [];
            if (txs.length === 0) {
                feed.innerHTML = '<div style="color: #64748b; font-size: 11px;">Citizens transiting between sectors. Next word-of-mouth hop pending...</div>';
                return;
            }
            feed.innerHTML = txs.slice().reverse().map(t => `
                <div style="background: #06090e; border-left: 3px solid #2dd4bf; border-radius: 0 6px 6px 0; padding: 5px 8px; font-size: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #2dd4bf; font-weight: bold;">📍 ${t.zone}</span>
                        <span style="color: #94a3b8; font-size: 9px;">${t.sentiment}</span>
                    </div>
                    <div style="color: #e2e8f0; margin-top: 2px;"><strong style="color: #38bdf8;">${t.speaker}</strong> spoke to <strong style="color: #facc15;">${t.listener}</strong>: '${t.topic}'</div>
                </div>
            `).join('');
        }

        function openCitizenCallModal() {
            document.getElementById('citizen-call-modal').style.display = 'flex';
        }

        function closeCitizenCallModal() {
            document.getElementById('citizen-call-modal').style.display = 'none';
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        }

        async function dialCitizenNow() {
            const cit = document.getElementById('call-citizen-select').value;
            const msg = document.getElementById('call-message-input').value;
            const transcript = document.getElementById('call-audio-transcript');
            const badge = document.getElementById('call-status-badge');
            if (badge) { badge.innerText = 'CONNECTING...'; badge.style.background = '#d97706'; }
            transcript.innerHTML = '<div style="color: #facc15;">📞 Connecting via Bengaluru Cellular Tower Network...</div>';

            try {
                const resp = await fetch('/api/citizen/call', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ citizen_name: cit, message: msg })
                });
                const res = await resp.json();
                if (badge) { badge.innerText = 'CONNECTED (LIVE)'; badge.style.background = '#10b981'; }
                transcript.innerHTML = `
                    <div style="color: #38bdf8; font-weight: bold; margin-bottom: 4px;">👤 ${res.citizen} (${res.role} • ${res.location}):</div>
                    <div style="color: #f1f5f9; font-size: 12px; margin-bottom: 6px;">"${res.spoken_response}"</div>
                    <div style="font-size: 10px; color: #10b981;">⚡ Double-entry wallet balance: ₹${res.wallet_inr.toLocaleString()}</div>
                `;
                if (VOICE_ENABLED && 'speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(res.spoken_response);
                    u.rate = 1.02;
                    u.pitch = 1.05;
                    window.speechSynthesis.speak(u);
                }
            } catch (e) {
                transcript.innerHTML = `<div style="color: #ef4444;">Call failed: ${e.message}</div>`;
                if (badge) { badge.innerText = 'CALL DROPPED'; badge.style.background = '#ef4444'; }
            }
        }

        function hangupCall() {
            const transcript = document.getElementById('call-audio-transcript');
            const badge = document.getElementById('call-status-badge');
            if (transcript) transcript.innerHTML += '<div style="color: #ef4444; margin-top: 6px;">[Call Ended by Governor]</div>';
            if (badge) { badge.innerText = 'LINE IDLE'; badge.style.background = '#64748b'; }
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        }

        async function fetchState() {
            try {
                const res = await fetch('/api/state');
                const data = await res.json();
                applyTickData(data);
            } catch (e) { console.error('fetchState error', e); }
        }




        async function fetchWorkspace() {
            try {
                const res = await fetch('/api/workspace');
                const files = await res.json();
                const wFeed = document.getElementById('workspace-feed');
                wFeed.innerHTML = Object.entries(files).map(([fname, content]) => `
                    <div class="workspace-card">
                        <div style="color: var(--orange); font-weight: bold; margin-bottom: 4px;">📄 ${fname}</div>
                        <div style="color: #c9d1d9; white-space: pre-wrap; max-height: 80px; overflow-y: auto;">${content}</div>
                    </div>
                `).join('');
            } catch (e) {}
        }

        async function sendGodCommand() {
            const input = document.getElementById('god-input');
            const target = document.getElementById('god-target').value;
            const text = input.value.trim();
            if (!text) return;

            if (target === 'ALL') {
                await fetch('/api/broadcast', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: text })
                });
                alert('👑 Governor Directive broadcast across all 100 Citizens of Bengaluru!');
            } else {
                const res = await fetch('/api/direct_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ persona_id: target, message: text })
                });
                const data = await res.json();
                alert(`💬 Direct response from ${data.persona_name} (${data.zone.replace(/_/g, ' ')}):\n\n"${data.persona_reply}"\n\nWallet: ₹${data.wallet} | Energy: ${data.energy}%`);
            }
            input.value = '';
            fetchState();
        }

        async function triggerMacro(actionType) {
            const res = await fetch('/api/macro_event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ event_type: actionType })
            });
            const data = await res.json();
            alert('⚡ ' + data.event);
            fetchState();
        }

        async function toggleAuto() {
            const res = await fetch('/api/toggle_auto', { method: 'POST' });
            const data = await res.json();
            isAutoRunning = data.auto_running;
            const btn = document.getElementById('btn-toggle');
            btn.innerText = isAutoRunning ? '⏸ Pause City' : '▶ Resume City';
            btn.className = isAutoRunning ? 'btn btn-pause' : 'btn';
        }

        async function stepManual() {
            await fetch('/api/step', { method: 'POST' });
            fetchState();
        }

        function openDirectoryModal() {
            if (!worldData || !worldData.persona_states) return;
            const grid = document.getElementById('dir-grid');
            grid.innerHTML = worldData.persona_states.map(p => `
                <div class="citizen-mini-card" onclick="inspectCitizen('${p.id}')">
                    <div style="font-weight: bold; color: var(--cyan);">${p.name}</div>
                    <div style="color: var(--text-muted); font-size: 10px;">${p.role}</div>
                    <div style="color: var(--orange); margin-top: 3px;">📍 ${p.zone.replace(/_/g, ' ')}</div>
                    <div style="color: var(--green); font-weight: bold; margin-top: 2px;">₹${p.wallet_inr} • ⚡ ${p.energy}%</div>
                </div>
            `).join('');
            document.getElementById('directory-modal').style.display = 'flex';
        }

        function closeDirectoryModal() {
            document.getElementById('directory-modal').style.display = 'none';
        }

        function filterDirectory() {
            const q = document.getElementById('dir-search').value.toLowerCase();
            const cards = document.querySelectorAll('.citizen-mini-card');
            cards.forEach(c => {
                c.style.display = c.innerText.toLowerCase().includes(q) ? 'block' : 'none';
            });
        }

        function inspectCitizen(pid) {
            if (!worldData || !worldData.persona_states) return;
            const p = worldData.persona_states.find(c => c.id === pid);
            if (!p) return;
            document.getElementById('modal-name').innerText = p.name;
            document.getElementById('modal-role').innerText = p.role;
            document.getElementById('modal-dept').innerText = p.department;
            document.getElementById('modal-zone').innerText = p.zone.replace(/_/g, ' ');
            document.getElementById('modal-wallet').innerText = '₹' + p.wallet_inr.toLocaleString();
            document.getElementById('modal-networth').innerText = '₹' + (p.net_worth || p.wallet_inr).toLocaleString();
            document.getElementById('modal-multiplier').innerText = p.doublings ? `(${2**p.doublings}x Multiplier)` : '';
            document.getElementById('modal-family').innerText = (p.marital_status === 'MARRIED') ? `💍 Married to ${p.partner_name || 'Partner'}` : ((p.marital_status === 'DATING') ? `❤️ Dating ${p.partner_name || 'Partner'}` : 'Single');
            document.getElementById('modal-kids').innerText = (p.children_count > 0) ? `🍼 ${p.children_count} Child(ren) enrolled in Bengaluru schools` : 'No kids yet (focusing on career)';
            document.getElementById('modal-happiness').innerText = `${p.happiness || 80}% Joy & Life Satisfaction`;
            const cBox = document.getElementById('modal-company-box');
            if (cBox) {
                if (p.has_company) {
                    cBox.style.display = 'block';
                    document.getElementById('modal-company').innerText = 'High-Tech Bangalore Startup / Unicorn';
                } else {
                    cBox.style.display = 'none';
                }
            }
            document.getElementById('modal-energy').innerText = p.energy + '%';
            document.getElementById('modal-action').innerText = p.action;

            const callBtn = document.getElementById('modal-call-btn');
            callBtn.onclick = async () => {
                const msg = prompt(`Enter directive or message to send directly to ${p.name}:`);
                if (msg) {
                    const res = await fetch('/api/direct_message', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ persona_id: p.id, message: msg })
                    });
                    const d = await res.json();
                    alert(`💬 ${p.name} says:\n\n"${d.persona_reply}"`);
                    closeModal();
                    fetchState();
                }
            };

            document.getElementById('citizen-modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('citizen-modal').style.display = 'none';
        }

        resizeCanvas();
        animateTrains();
        fetchState();
        fetchWorkspace();

        // ── LIVE UPDATES via Server-Sent Events ─────────────────────────
        // SSE fires on every backend tick (~8s). On each event:
        //   • All metrics, stocks, radio, chronicle, voxel, p2p update instantly
        //   • 2D canvas redraws
        //   • 3D engine citizens sync
        let sseReconnectDelay = 1000;
        let sseActive = false;
        function connectSSE() {
            const es = new EventSource('/api/stream');
            es.onopen = function() { sseActive = true; };
            es.onmessage = function(evt) {
                try {
                    const data = JSON.parse(evt.data);
                    applyTickData(data);
                    sseReconnectDelay = 1000; // reset backoff on success
                    sseActive = true;
                } catch(e) { console.warn('SSE parse error', e); }
            };
            es.onerror = function() {
                sseActive = false;
                es.close();
                // exponential backoff fallback
                setTimeout(connectSSE, sseReconnectDelay);
                sseReconnectDelay = Math.min(sseReconnectDelay * 2, 30000);
            };
        }
        connectSSE();

        // ── FAST POLLS (fallback + conversation/event freshness) ─────────
        // These run independently from SSE so conversations always feel live.
        async function fetchConversations() {
            if (sseActive) return;
            try {
                const res = await fetch('/api/conversations');
                const convs = await res.json();
                renderDialogues(convs);
            } catch(e) {}
        }

        async function fetchEvents() {
            if (sseActive) return;
            try {
                const res = await fetch('/api/events');
                const evts = await res.json();
                renderEvents(evts);
            } catch(e) {}
        }

        // Separate metric-only poll as SSE safety net
        // ── SYNTHETIC FOCUS GROUP & MARKETING STUDIO JS ────────────────────
        function renderMarketingStudio(analytics) {
            if (!analytics) return;
            const revEl = document.getElementById('mkt-total-revenue');
            if (revEl) revEl.innerText = analytics.total_market_revenue || '₹0';

            const cList = document.getElementById('campaigns-list');
            if (cList && analytics.campaigns) {
                cList.innerHTML = analytics.campaigns.map(c => `
                    <div style="background: #090e15; border: 1px solid ${c.variant.includes('A') ? 'rgba(56,189,248,0.4)' : 'rgba(168,85,247,0.4)'}; border-radius: 6px; padding: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <div style="font-weight: bold; color: #fff; font-size: 11px;">
                                ${c.name}
                                <span style="font-size: 9px; padding: 1px 5px; border-radius: 8px; background: ${c.variant.includes('A') ? '#0284c7' : '#7c3aed'}; color: #fff; margin-left: 4px;">${c.variant}</span>
                            </div>
                            <span style="font-size: 10px; font-weight: bold; color: #10b981;">₹${c.price_inr.toLocaleString()}</span>
                        </div>
                        <div style="font-size: 10px; color: #94a3b8; font-style: italic; margin-bottom: 6px;">"${c.tagline}"</div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; text-align: center; background: #06090e; padding: 4px; border-radius: 4px; font-size: 9px;">
                            <div>
                                <div style="color: #64748b;">IMPR</div>
                                <div style="color: #cbd5e1; font-weight: bold;">${c.impressions}</div>
                            </div>
                            <div>
                                <div style="color: #64748b;">CLICKS (CTR)</div>
                                <div style="color: #38bdf8; font-weight: bold;">${c.clicks} (${c.ctr_percent}%)</div>
                            </div>
                            <div>
                                <div style="color: #64748b;">BUYS (CVR)</div>
                                <div style="color: #10b981; font-weight: bold;">${c.purchases} (${c.cvr_percent}%)</div>
                            </div>
                            <div>
                                <div style="color: #64748b;">REVENUE</div>
                                <div style="color: #facc15; font-weight: bold;">${c.revenue_inr}</div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 9px;">
                            <span style="color: ${c.k_factor >= 1.0 ? '#10b981' : '#f59e0b'}; font-weight: bold;">Viral K: ${c.k_factor}x</span>
                            <span style="color: ${c.nps_score >= 0 ? '#38bdf8' : '#ef4444'};"><strong style="color: #64748b;">NPS:</strong> ${c.nps_score}</span>
                            <span style="color: #a855f7; font-weight: bold;">${c.verdict}</span>
                        </div>
                    </div>
                `).join('');
            }

            const objPills = document.getElementById('objection-pills');
            if (objPills && analytics.objection_breakdown) {
                const totalObj = Object.values(analytics.objection_breakdown).reduce((a, b) => a + b, 0) || 1;
                objPills.innerHTML = Object.entries(analytics.objection_breakdown).map(([k, v]) => `
                    <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 2px 6px; border-radius: 4px;">
                        ${k.replace('_', ' ')}: <strong>${v}</strong> (${Math.round(v/totalObj*100)}%)
                    </span>
                `).join('');
            }

            const mFeed = document.getElementById('monologue-feed');
            if (mFeed && analytics.recent_monologues) {
                mFeed.innerHTML = analytics.recent_monologues.slice(0, 10).map(m => {
                    const isBuy = m.decision === 'PURCHASED';
                    return `
                        <div style="border-left: 3px solid ${isBuy ? '#10b981' : '#ef4444'}; padding-left: 6px; margin-bottom: 4px;">
                            <div style="display: flex; justify-content: space-between; font-size: 10px;">
                                <strong style="color: #fff;">${m.citizen_name}</strong>
                                <span style="color: ${isBuy ? '#10b981' : '#f87171'}; font-weight: bold;">${m.decision}</span>
                            </div>
                            <div style="color: #94a3b8; font-size: 10px; margin-top: 1px;">${m.thought_monologue}</div>
                        </div>
                    `;
                }).join('');
            }
        }

        async function runSyntheticFocusGroup() {
            const q = document.getElementById('fg-question-input').value.trim();
            const cohort = document.getElementById('fg-cohort-select').value;
            const resBox = document.getElementById('fg-results-box');
            if (!q) return;

            resBox.innerHTML = '<div style="color: #facc15; padding: 6px;">⚡ Interrogating 100 personas across Bangalore airwaves (System-2 Wallet & Skepticism Test)...</div>';
            try {
                const res = await fetch('/api/campaign/focus_group', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ question: q, cohort_filter: cohort })
                });
                const data = await res.json();
                const s = data.summary;
                const isFail = s.is_commercial_failure;
                const autopsy = s.financial_autopsy || {};
                const mistakes = s.mistakes_made || [];

                resBox.innerHTML = `
                    <div style="background: ${isFail ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)'}; border: 1px solid ${isFail ? '#ef4444' : '#10b981'}; padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                        <div style="font-weight: 800; font-size: 11px; color: ${isFail ? '#f87171' : '#34d399'};">
                            ${s.consensus_verdict}
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; text-align: center; margin-top: 6px; font-size: 9px;">
                            <div style="background: #0b1320; padding: 4px; border-radius: 4px; color: #10b981;"><strong>Favor:</strong> ${s.enthusiastic_percent}%</div>
                            <div style="background: #0b1320; padding: 4px; border-radius: 4px; color: #facc15;"><strong>Skeptical:</strong> ${s.skeptical_percent}%</div>
                            <div style="background: #0b1320; padding: 4px; border-radius: 4px; color: #f87171;"><strong>Price Res:</strong> ${s.price_resistant_percent}%</div>
                            <div style="background: #0b1320; padding: 4px; border-radius: 4px; color: #94a3b8;"><strong>Pass:</strong> ${s.strong_pass_percent}%</div>
                        </div>

                        ${isFail && mistakes.length > 0 ? `
                        <div style="margin-top: 8px; border-top: 1px solid rgba(239, 68, 68, 0.3); padding-top: 6px;">
                            <div style="font-size: 10px; font-weight: bold; color: #fca5a5; margin-bottom: 4px;">⚠️ 5 FATAL MISTAKES MADE BY THE BRAND/FOUNDER:</div>
                            <div style="display: flex; flex-direction: column; gap: 3px; font-size: 9.5px; color: #fed7aa;">
                                ${mistakes.map(m => `<div>• ${m}</div>`).join('')}
                            </div>
                        </div>
                        ` : ''}

                        ${autopsy.projected_cac_inr ? `
                        <div style="margin-top: 6px; background: #06090e; padding: 5px 8px; border-radius: 4px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; font-size: 9px; text-align: center;">
                            <div><span style="color: #94a3b8;">Proj CAC:</span> <strong style="color: #f87171;">₹${autopsy.projected_cac_inr.toLocaleString()}</strong></div>
                            <div><span style="color: #94a3b8;">Proj LTV:</span> <strong style="color: #38bdf8;">₹${autopsy.projected_ltv_inr.toLocaleString()}</strong></div>
                            <div><span style="color: #94a3b8;">Runway Burn:</span> <strong style="color: #f59e0b;">${autopsy.burn_kill_horizon_days}d</strong></div>
                        </div>
                        ` : ''}

                        ${s.honest_prescription ? `
                        <div style="margin-top: 6px; font-size: 9.5px; color: #e2e8f0; font-style: italic; background: rgba(0,0,0,0.3); padding: 4px 6px; border-radius: 4px;">
                            <strong style="color: #fbbf24;">⚡ Unvarnished Prescription:</strong> ${s.honest_prescription}
                        </div>
                        ` : ''}
                    </div>

                    <div style="font-size: 10px; font-weight: bold; color: #94a3b8; margin-bottom: 4px;">UNFILTERED CITIZEN REJECTIONS & TESTIMONIALS:</div>
                    <div style="display: flex; flex-direction: column; gap: 4px; max-height: 180px; overflow-y: auto;">
                        ${data.quotes.slice(0, 6).map(qt => `
                            <div style="background: #0d1520; border-left: 3px solid ${qt.bucket === 'ENTHUSIASTIC_BUYER' ? '#10b981' : qt.bucket === 'PRICE_RESISTANT' ? '#f87171' : '#facc15'}; padding: 4px 8px; border-radius: 4px;">
                                <div style="display: flex; justify-content: space-between; font-size: 9.5px;">
                                    <strong style="color: #e2e8f0;">${qt.citizen_name} (${qt.role} • ${qt.department})</strong>
                                    <span style="font-size: 8.5px; color: #94a3b8;">${qt.bucket.replace('_', ' ')}</span>
                                </div>
                                <div style="color: #cbd5e1; font-style: italic; font-size: 9px; margin-top: 2px;">"${qt.quote}"</div>
                            </div>
                        `).join('')}
                    </div>
                `;

                if (data.visual_creative) {
                    const c = data.visual_creative;
                    const cr = c.critique || {};
                    const container = document.getElementById('visual-ad-container');
                    const critiqueBox = document.getElementById('visual-ad-critique');
                    if (container) container.innerHTML = c.svg_markup || '';
                    if (critiqueBox) {
                        critiqueBox.innerHTML = `
                            <div style="background: #090e15; padding: 4px; border-radius: 4px; color: #38bdf8;"><strong>Rating:</strong> ${cr.overall_design_rating || '8.2/10'}</div>
                            <div style="background: #090e15; padding: 4px; border-radius: 4px; color: #a78bfa;"><strong>Appeal:</strong> ${cr.visual_appeal || '8.5/10'}</div>
                            <div style="background: #090e15; padding: 4px; border-radius: 4px; color: #34d399;"><strong>Legibility:</strong> ${cr.typography_legibility || '9.0/10'}</div>
                            <div style="background: #090e15; padding: 4px; border-radius: 4px; color: #fbbf24;"><strong>Trust:</strong> ${cr.brand_trust_index || '8.0/10'}</div>
                        `;
                    }
                }
            } catch (e) {
                resBox.innerHTML = '<div style="color: #ef4444; padding: 6px;">Focus group error: ' + e + '</div>';
            }
        }

        async function warpTime(hour, minute) {
            try {
                const res = await fetch('/api/set_time', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ hour: hour, minute: minute })
                });
                const data = await res.json();
                applyTickData(data);
            } catch (e) {
                console.error('Time warp failed:', e);
            }
        }

        async function stepSimNow() {
            try {
                const res = await fetch('/api/step', { method: 'POST' });
                const data = await res.json();
                applyTickData(data);
            } catch (e) {
                console.error('Step simulation failed:', e);
            }
        }

        let currentTVChannel = 'BLR24_NEWS';
        function switchTVChannel(chanId) {
            currentTVChannel = chanId;
            ['blr24', 'cnbc', 'ai'].forEach(k => {
                const b = document.getElementById('tv-btn-' + k);
                if (b) { b.style.borderColor = 'var(--border)'; b.style.color = '#c9d1d9'; }
            });
            const activeBtn = document.getElementById(chanId === 'BLR24_NEWS' ? 'tv-btn-blr24' : chanId === 'CNBC_BLR_TECH' ? 'tv-btn-cnbc' : 'tv-btn-ai');
            if (activeBtn) {
                activeBtn.style.borderColor = chanId === 'BLR24_NEWS' ? '#ef4444' : chanId === 'CNBC_BLR_TECH' ? '#10b981' : '#8b5cf6';
                activeBtn.style.color = chanId === 'BLR24_NEWS' ? '#fca5a5' : chanId === 'CNBC_BLR_TECH' ? '#a7f3d0' : '#ddd6fe';
            }
            if (worldData && worldData.tv_broadcast) renderLiveTV(worldData.tv_broadcast);
        }

        function renderLiveTV(tvData) {
            if (!tvData || !tvData.channels) return;
            const chan = tvData.channels.find(c => c.id === currentTVChannel) || tvData.channels[0];
            if (!chan) return;
            const titleEl = document.getElementById('tv-show-title');
            const anchorEl = document.getElementById('tv-anchor-name');
            const studioEl = document.getElementById('tv-studio-loc');
            const teleEl = document.getElementById('tv-teleprompter');
            const tickerEl = document.getElementById('tv-ticker-text');

            if (titleEl) titleEl.innerText = chan.name + ' • ' + chan.current_show;
            if (anchorEl) anchorEl.innerText = '— ' + chan.anchor;
            if (studioEl) studioEl.innerText = chan.location;
            if (teleEl) teleEl.innerText = '"' + chan.studio_dialogue + '"';
            if (tickerEl && chan.breaking_ticker) {
                tickerEl.innerText = chan.breaking_ticker.join('  ★  ');
            }
        }

        function renderRealIntel(intel) {
            if (!intel) return;
            const wEl = document.getElementById('real-weather-val');
            const fxEl = document.getElementById('real-forex-val');
            const hnEl = document.getElementById('real-hn-val');
            if (wEl && intel.weather) wEl.innerText = `${intel.weather.temperature_c}°C • ${intel.weather.condition}`;
            if (fxEl && intel.finance) fxEl.innerText = `₹${intel.finance.usd_inr} / USD`;
            if (hnEl && intel.global_tech_news && intel.global_tech_news.length > 0) {
                hnEl.innerText = intel.global_tech_news[0].title.slice(0, 34) + '...';
            }
        }

        let currentSocialTab = 'pulse';
        function switchSocialTab(tab) {
            currentSocialTab = tab;
            ['pulse', 'groups', 'reddit', 'places'].forEach(t => {
                const btn = document.getElementById('social-tab-' + t);
                const panel = document.getElementById('panel-social-' + t);
                if (btn) {
                    btn.style.borderColor = t === tab ? '#38bdf8' : 'var(--border)';
                    btn.style.color = t === tab ? '#38bdf8' : '#c9d1d9';
                }
                if (panel) panel.style.display = t === tab ? 'flex' : 'none';
            });
            if (worldData && worldData.social_pulse) renderSocialPulse(worldData.social_pulse);
        }

        async function postGovernorTweet() {
            const input = document.getElementById('gov-tweet-input');
            const text = input.value.trim();
            if (!text) return;
            try {
                await fetch('/api/social/post', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text: text })
                });
                input.value = '';
                if (worldData && worldData.social_pulse) {
                    worldData.social_pulse.tweets.unshift({
                        handle: '@Governor_Lalith',
                        name: 'Lalith (City Governor)',
                        badge: '⚡ CITY GOVERNOR',
                        text: text,
                        likes: 194,
                        retweets: 62,
                        time: 'Just now',
                        tags: ['#GovernorDirective', '#BengaluruMetropolis']
                    });
                    renderSocialPulse(worldData.social_pulse);
                }
            } catch (e) {
                console.error('Tweet error:', e);
            }
        }

        function renderSocialPulse(social) {
            if (!social) return;
            const trendsBar = document.getElementById('social-trends-bar');
            if (trendsBar && social.trending_hashtags) {
                trendsBar.innerHTML = social.trending_hashtags.map(th => `
                    <span style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #7dd3fc; padding: 2px 6px; border-radius: 4px; font-weight: bold;">
                        ${th.tag} (${th.tweets_count})
                    </span>
                `).join('');
            }

            const tweetsFeed = document.getElementById('social-tweets-feed');
            if (tweetsFeed && social.tweets) {
                tweetsFeed.innerHTML = social.tweets.map(tw => `
                    <div style="background: #090e15; border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px; font-size: 11px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <strong style="color: #fff;">${tw.name}</strong>
                                <span style="color: #64748b; font-size: 10px;">${tw.handle}</span>
                                <span style="background: rgba(188, 140, 255, 0.15); color: var(--purple); padding: 1px 4px; border-radius: 3px; font-size: 8.5px;">${tw.badge}</span>
                            </div>
                            <span style="color: #64748b; font-size: 9px;">${tw.time}</span>
                        </div>
                        <div style="color: #cbd5e1; margin-bottom: 4px;">${tw.text}</div>
                        <div style="display: flex; gap: 12px; font-size: 9.5px; color: #64748b;">
                            <span>❤️ ${tw.likes}</span>
                            <span>🔁 ${tw.retweets}</span>
                            <span style="color: #38bdf8;">💬 Reply</span>
                        </div>
                    </div>
                `).join('');
            }

            const groupsList = document.getElementById('community-groups-list');
            if (groupsList && social.community_groups) {
                groupsList.innerHTML = social.community_groups.map(g => `
                    <div style="background: #090e15; border: 1px solid var(--border); border-radius: 6px; padding: 8px; font-size: 11px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: #38bdf8;">${g.name}</strong>
                            <span style="color: #10b981; font-size: 10px;">👥 ${g.members_count} active</span>
                        </div>
                        <div style="color: #8b949e; font-size: 10px; margin: 2px 0 6px;">${g.description}</div>
                        <div style="background: #06090e; padding: 6px; border-radius: 4px; border-left: 2px solid var(--yellow);">
                            <span style="color: #facc15; font-weight: bold; font-size: 9.5px;">${g.recent_chatter[0].sender} (${g.recent_chatter[0].role}):</span>
                            <span style="color: #cbd5e1; font-style: italic; font-size: 9.5px;">"${g.recent_chatter[0].text}"</span>
                        </div>
                    </div>
                `).join('');
            }

            const redditList = document.getElementById('reddit-threads-list');
            if (redditList && social.reddit_threads) {
                redditList.innerHTML = social.reddit_threads.map(r => `
                    <div style="background: #090e15; border: 1px solid var(--border); border-radius: 6px; padding: 8px; font-size: 11px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
                            <span style="background: rgba(240, 136, 62, 0.15); color: var(--orange); padding: 1px 5px; border-radius: 3px; font-size: 9px; font-weight: bold;">${r.flair}</span>
                            <span style="color: #64748b; font-size: 9.5px;">Posted by ${r.author}</span>
                        </div>
                        <strong style="color: #fff; font-size: 11px;">${r.title}</strong>
                        <div style="color: #94a3b8; font-size: 10px; margin-top: 3px;">${r.snippet}</div>
                        <div style="display: flex; gap: 10px; margin-top: 5px; font-size: 9.5px; color: #38bdf8;">
                            <span>⬆️ ${r.upvotes} Upvotes</span>
                            <span>💬 ${r.comments_count} Comments</span>
                        </div>
                    </div>
                `).join('');
            }

            const placesList = document.getElementById('community-places-list');
            if (placesList && worldData && worldData.community_places) {
                const cp = worldData.community_places;
                placesList.innerHTML = `
                    <div style="background: #090e15; padding: 8px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.3);">
                        <strong style="color: #f59e0b;">🛕 Temples & Heritage:</strong>
                        <ul style="margin: 4px 0 0 14px; color: #cbd5e1; font-size: 10px;">
                            ${(cp.temples || []).map(t => `<li>${t}</li>`).join('')}
                        </ul>
                    </div>
                    <div style="background: #090e15; padding: 8px; border-radius: 6px; border: 1px solid rgba(96, 165, 250, 0.3);">
                        <strong style="color: #60a5fa;">⛪ Churches & Fellowship:</strong>
                        <ul style="margin: 4px 0 0 14px; color: #cbd5e1; font-size: 10px;">
                            ${(cp.churches || []).map(c => `<li>${c}</li>`).join('')}
                        </ul>
                    </div>
                    <div style="background: #090e15; padding: 8px; border-radius: 6px; border: 1px solid rgba(236, 72, 153, 0.3);">
                        <strong style="color: #ec4899;">🏘️ Housing & Co-Living:</strong>
                        <ul style="margin: 4px 0 0 14px; color: #cbd5e1; font-size: 10px;">
                            ${(cp.housing || []).map(h => `<li>${h}</li>`).join('')}
                        </ul>
                    </div>
                    <div style="background: #090e15; padding: 8px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">
                        <strong style="color: #10b981;">🏥 Hospitals & Care Clinics:</strong>
                        <ul style="margin: 4px 0 0 14px; color: #cbd5e1; font-size: 10px;">
                            ${(cp.care_centers || []).map(m => `<li>${m}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }

        function openLaunchCampaignModal() {
            document.getElementById('launch-campaign-modal').classList.add('active');
        }
        function closeLaunchCampaignModal() {
            document.getElementById('launch-campaign-modal').classList.remove('active');
        }
        async function submitLaunchCampaign() {
            const name = document.getElementById('mkt-new-name').value.trim();
            const tagline = document.getElementById('mkt-new-tagline').value.trim();
            const sector = document.getElementById('mkt-new-sector').value;
            const price = parseFloat(document.getElementById('mkt-new-price').value) || 1999.0;
            const utility = parseFloat(document.getElementById('mkt-new-utility').value) || 8.0;
            const quality = parseFloat(document.getElementById('mkt-new-quality').value) || 8.0;

            await fetch('/api/campaign/launch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name,
                    tagline: tagline,
                    sector: sector,
                    price_inr: price,
                    claimed_utility: utility,
                    actual_quality: quality
                })
            });
            closeLaunchCampaignModal();
            fetchState();
        }

        function openABTestModal() {
            document.getElementById('ab-test-modal').classList.add('active');
        }
        function closeABTestModal() {
            document.getElementById('ab-test-modal').classList.remove('active');
        }
        async function submitABTest() {
            const name = document.getElementById('ab-name').value.trim();
            const tagA = document.getElementById('ab-tagline-a').value.trim();
            const priceA = parseFloat(document.getElementById('ab-price-a').value) || 1499.0;
            const tagB = document.getElementById('ab-tagline-b').value.trim();
            const priceB = parseFloat(document.getElementById('ab-price-b').value) || 2499.0;

            await fetch('/api/campaign/ab_test', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name,
                    sector: 'TECH_DEV_TOOL',
                    variant_a_tagline: tagA,
                    variant_a_price: priceA,
                    variant_b_tagline: tagB,
                    variant_b_price: priceB
                })
            });
            closeABTestModal();
            fetchState();
        }

        // ── CITIZEN PHONE INSPECTOR MODAL ─────────────────────────
        async function openCitizenPhoneModal(cid) {
            document.getElementById('citizen-phone-modal').style.display = 'flex';
            populateCitizenDropdowns();
            if (cid) {
                document.getElementById('phone-citizen-select').value = cid;
            }
            await loadCitizenPhone(cid || 'c1');
        }

        function closeCitizenPhoneModal() {
            document.getElementById('citizen-phone-modal').style.display = 'none';
        }

        async function loadCitizenPhone(cid) {
            try {
                const res = await fetch('/api/citizen/phone?id=' + cid);
                const p = await res.json();
                if (!p) return;
                const model = p.phone_model || p.model || 'Pixel 8 Pro';
                const carrier = p.carrier || 'Airtel 5G Plus';
                const batt = (p.battery_percent !== undefined) ? p.battery_percent : (p.battery_level || 88);
                const upiBal = p.upi_balance_inr || 24500;
                const upiId = p.upi_id || (p.citizen_name ? p.citizen_name.toLowerCase().replace(/ /g, '.') + '@oksbi' : 'citizen@oksbi');

                document.getElementById('phone-clock').innerText = worldData ? worldData.world_time : '09:15 AM';
                document.getElementById('phone-carrier').innerText = carrier;
                document.getElementById('phone-battery').innerText = '🔋 ' + batt + '%';
                document.getElementById('phone-model-name').innerText = model + (p.color_finish ? ' • ' + p.color_finish : '');
                document.getElementById('phone-os-version').innerText = (p.os_version || 'Android 14') + ' • 5G Ultra-Broadband';
                document.getElementById('phone-upi-balance').innerText = '₹' + Number(upiBal).toLocaleString();
                document.getElementById('phone-upi-id').innerText = upiId;

                const tContainer = document.getElementById('phone-chat-threads');
                const threads = p.whatsapp_threads || p.chat_threads || [];
                if (tContainer && threads.length) {
                    tContainer.innerHTML = threads.map(t => `
                        <div style="border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 4px;">
                            <div style="display:flex; justify-content:space-between; color:#fff; font-weight:bold;">
                                <span>${t.name || t.contact}</span>
                                <span style="font-size:9px; color:#64748b;">${t.time}</span>
                            </div>
                            <div style="color:#94a3b8; font-style:italic;">"${t.last_msg}"</div>
                        </div>
                    `).join('');
                }

                const rContainer = document.getElementById('phone-transactions-list');
                const txs = p.recent_upi_transactions || p.food_delivery_orders || [];
                if (rContainer && txs.length) {
                    rContainer.innerHTML = txs.map(o => `
                        <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:3px;">
                            <span>${o.title || o.vendor} (${o.category || o.item || 'UPI Payment'})</span>
                            <span style="color:#10b981; font-weight:bold;">₹${o.amount_inr || o.price_inr}</span>
                        </div>
                    `).join('');
                }
            } catch(e) { console.error('Error loading phone', e); }
        }

        // ── CITIZEN HOUSING INSPECTOR MODAL ───────────────────────
        async function openCitizenHousingModal(cid) {
            document.getElementById('citizen-housing-modal').style.display = 'flex';
            populateCitizenDropdowns();
            if (cid) {
                document.getElementById('housing-citizen-select').value = cid;
            }
            await loadCitizenHousing(cid || 'c1');
        }

        function closeCitizenHousingModal() {
            document.getElementById('citizen-housing-modal').style.display = 'none';
        }

        async function loadCitizenHousing(cid) {
            try {
                const res = await fetch('/api/citizen/home?id=' + cid);
                const h = await res.json();
                if (!h || !h.community_name) return;
                document.getElementById('house-complex-name').innerText = h.community_name + ' (' + h.housing_type + ')';
                document.getElementById('house-address').innerText = h.full_address;
                document.getElementById('house-monthly-rent').innerText = '₹' + Number(h.monthly_rent_inr).toLocaleString() + ' / month';
                document.getElementById('house-lease-type').innerText = h.is_owner ? 'Registered Freehold (Owner)' : 'Residential Lease (Tenant)';
                
                const badge = document.getElementById('house-occupancy-badge');
                if (badge) {
                    badge.innerText = h.current_occupancy;
                    badge.style.background = h.current_occupancy === 'SLEEPING_IN_BED' ? '#4c1d95' : '#064e3b';
                }

                const fList = document.getElementById('house-furnishings-list');
                if (fList && h.room_furnishings) {
                    fList.innerHTML = h.room_furnishings.map(item => `<div>• ${item}</div>`).join('');
                }
            } catch(e) { console.error('Error loading housing', e); }
        }

        // ── URBAN FAUNA PETTING ACTION ────────────────────────────
        async function quickPetAnimal(animalId, animalName) {
            try {
                const res = await fetch('/api/fauna/interact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        citizen_name: 'Aarav Sharma',
                        animal_id: animalId,
                        action: 'PET'
                    })
                });
                const data = await res.json();
                const feed = document.getElementById('fauna-interactions-feed');
                if (feed && data.message) {
                    const el = document.createElement('div');
                    el.style.color = '#fbbf24';
                    el.style.fontWeight = 'bold';
                    el.innerHTML = `✨ <em>${data.animal}</em>: ${data.message}`;
                    feed.prepend(el);
                }
            } catch(e) { console.error('Error petting fauna', e); }
        }

        function populateCitizenDropdowns() {
            if (!worldData || !worldData.citizens) return;
            const pSelect = document.getElementById('phone-citizen-select');
            const hSelect = document.getElementById('housing-citizen-select');
            if (pSelect && pSelect.options.length <= 1) {
                pSelect.innerHTML = worldData.citizens.map(c => `<option value="${c.id}">${c.name} (${c.role.slice(0, 24)})</option>`).join('');
            }
            if (hSelect && hSelect.options.length <= 1) {
                hSelect.innerHTML = worldData.citizens.map(c => `<option value="${c.id}">${c.name} (${c.role.slice(0, 24)})</option>`).join('');
            }
        }

        // Smart Fallback Polling (only polls when SSE is inactive)
        setInterval(() => {
            if (!sseActive) fetchState();
        }, 5000);
        setInterval(fetchConversations, 8000); // conversations
        setInterval(fetchEvents, 8000);        // events feed
        setInterval(fetchWorkspace, 25000);    // workspace files slower
    </script>
</body>
</html>
"""

class WorldHandler(SimpleHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200):
        encoded = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(encoded)
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif parsed.path == "/api/state":
            accept_enc = self.headers.get("Accept-Encoding", "")
            with WORLD_LOCK:
                gz_data = LAST_TELEMETRY_GZIP
                raw_data = LAST_TELEMETRY_BYTES
            if "gzip" in accept_enc and gz_data:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Length", str(len(gz_data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(gz_data)
                self.wfile.flush()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw_data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(raw_data)
                self.wfile.flush()
        elif parsed.path.startswith("/api/zone_blocks"):
            query_params = {}
            if "?" in self.path:
                qstr = self.path.split("?", 1)[1]
                query_params = dict(q.split("=") for q in qstr.split("&") if "=" in q)
            zone = query_params.get("zone", "Manyata_Tech_Park")
            blocks = WORLD.voxel_world.get_zone_blocks(zone)
            self._send_json({"zone": zone, "blocks": blocks})
        elif parsed.path == "/api/tv/channels":
            with WORLD_LOCK:
                tv_data = WORLD.tv_network.get_all_channels()
            self._send_json(tv_data)
        elif parsed.path == "/api/social/feed":
            with WORLD_LOCK:
                s_data = WORLD.social_os.get_social_state()
            self._send_json(s_data)
        elif parsed.path == "/api/realtime/intel":
            with WORLD_LOCK:
                i_data = WORLD.realtime_harvester.get_intel()
            self._send_json(i_data)
        elif parsed.path in ("/api/stream", "/api/sse"):
            # Server-Sent Events — push on every world tick with TCP_NODELAY and Keepalive
            try:
                self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except Exception:
                pass
            client_q = _queue.Queue(maxsize=4)
            with SSE_LOCK:
                SSE_SUBSCRIBERS.append(client_q)
            self.send_response(200)
            self.send_header("Content-type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            # Send current pre-serialized state immediately so browser doesn't wait
            try:
                with WORLD_LOCK:
                    init_payload = LAST_TELEMETRY_SSE if LAST_TELEMETRY_SSE else ("data: " + json.dumps(LAST_TELEMETRY) + "\n\n").encode()
                self.wfile.write(init_payload)
                self.wfile.flush()
            except Exception:
                pass
            while not SHUTDOWN_EVENT.is_set():
                try:
                    chunk = client_q.get(timeout=15)
                    self.wfile.write(chunk)
                    self.wfile.flush()
                except _queue.Empty:
                    # Heartbeat keepalive
                    try:
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
                    except Exception:
                        break
                except Exception:
                    break
            with SSE_LOCK:
                try:
                    SSE_SUBSCRIBERS.remove(client_q)
                except ValueError:
                    pass
            return
        elif parsed.path == "/api/conversations":
            limit = 20
            try:
                convs = WORLD.get_recent_conversations(limit=limit)
            except Exception:
                with WORLD_LOCK:
                    convs = LAST_TELEMETRY.get("recent_conversations", [])
            self._send_json(convs)
        elif parsed.path == "/api/events":
            try:
                evts = WORLD.get_recent_events(limit=30)
            except Exception:
                with WORLD_LOCK:
                    evts = LAST_TELEMETRY.get("recent_events", [])
            self._send_json(evts)
        elif parsed.path == "/api/campaigns":
            with WORLD_LOCK:
                data = WORLD.consumer_marketing.get_campaign_analytics()
            self._send_json(data)
        elif parsed.path == "/api/sandbox":
            with WORLD_LOCK:
                s_runs = WORLD.sandbox_engine.get_recent_runs()
            self._send_json(s_runs)
        elif parsed.path == "/api/lifecycle":
            with WORLD_LOCK:
                l_stats = WORLD.lifecycle_engine.get_lifecycle_stats()
            self._send_json(l_stats)
        elif parsed.path == "/api/diffusion":
            with WORLD_LOCK:
                d_hops = WORLD.spatial_diffusion.step_spatial_diffusion(WORLD.personas, WORLD.tick_count)
            self._send_json(d_hops)
        elif parsed.path == "/api/workspace":
            now = time.time()
            if now - WORKSPACE_CACHE.get("timestamp", 0.0) < 5.0 and WORKSPACE_CACHE.get("data"):
                self._send_json(WORKSPACE_CACHE["data"])
            else:
                workspace_files = {}
                for fname in ["bengaluru_chronicle_tabloid.md", "bengaluru_cloud_architecture.md", "electronic_city_security_audit.log", "indiranagar_startup_pulse.json"]:
                    fpath = os.path.join(WORKSPACE_DIR, fname)
                    if os.path.exists(fpath):
                        try:
                            with open(fpath, "r") as f:
                                workspace_files[fname] = f.read()[-500:]
                        except Exception:
                            pass
                WORKSPACE_CACHE["timestamp"] = now
                WORKSPACE_CACHE["data"] = workspace_files
                self._send_json(workspace_files)
        elif parsed.path == "/api/citizen/phone":
            query_params = {}
            if "?" in self.path:
                qstr = self.path.split("?", 1)[1]
                query_params = dict(q.split("=") for q in qstr.split("&") if "=" in q)
            cid = query_params.get("id", "AARAV")
            with WORLD_LOCK:
                p_data = WORLD.smartphone_engine.get_citizen_phone(cid)
                if not p_data:
                    for k, v in WORLD.smartphone_engine.smartphones.items():
                        if k.lower() == cid.lower() or v.get("citizen_name", "").lower() == cid.lower():
                            p_data = v
                            break
                if not p_data and WORLD.smartphone_engine.smartphones:
                    p_data = list(WORLD.smartphone_engine.smartphones.values())[0]
            self._send_json(p_data or {})
        elif parsed.path == "/api/citizen/home":
            query_params = {}
            if "?" in self.path:
                qstr = self.path.split("?", 1)[1]
                query_params = dict(q.split("=") for q in qstr.split("&") if "=" in q)
            cid = query_params.get("id", "AARAV")
            with WORLD_LOCK:
                h_data = WORLD.housing_engine.get_citizen_home(cid)
                if not h_data:
                    for k, v in WORLD.housing_engine.citizen_homes.items():
                        if k.lower() == cid.lower() or v.get("citizen_name", "").lower() == cid.lower():
                            h_data = v
                            break
                if not h_data and WORLD.housing_engine.citizen_homes:
                    h_data = list(WORLD.housing_engine.citizen_homes.values())[0]
            self._send_json(h_data or {})
        elif parsed.path == "/api/fauna/state":
            with WORLD_LOCK:
                f_data = {
                    "dogs": WORLD.fauna_engine.dogs,
                    "cats": WORLD.fauna_engine.cats,
                    "parks": WORLD.fauna_engine.parks,
                    "recent_interactions": WORLD.fauna_engine.recent_interactions[-10:]
                }
            self._send_json(f_data)
        elif parsed.path.startswith("/static/"):
            file_path = os.path.join("/Users/lalith/ray_agent_world", parsed.path[1:])
            if os.path.exists(file_path):
                self.send_response(200)
                if file_path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript")
                elif file_path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif file_path.endswith(".json"):
                    self.send_header("Content-type", "application/json")
                else:
                    self.send_header("Content-type", "image/png")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        global LAST_TELEMETRY, AUTO_RUNNING
        parsed = urlparse(self.path)
        if parsed.path == "/api/command":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            cmd = body.get("command", "")
            params = body.get("params", {})
            res = {"status": "error", "message": f"Unknown command: {cmd}"}
            if cmd == "broadcast":
                with WORLD_LOCK:
                    res = WORLD.broadcast_executive_directive(params.get("message", ""))
            elif cmd == "macro_event":
                with WORLD_LOCK:
                    res = WORLD.trigger_macro_event(params.get("event_type", "MONSOON_FLOOD"))
            elif cmd == "step":
                with WORLD_LOCK:
                    new_data = WORLD.step()
                    LAST_TELEMETRY = new_data
                update_telemetry_cache(new_data)
                _push_sse(new_data)
                res = {"status": "ok", "tick": new_data.get("tick")}
            elif cmd == "toggle_auto":
                AUTO_RUNNING = not AUTO_RUNNING
                res = {"status": "ok", "auto_running": AUTO_RUNNING}
            elif cmd == "set_time":
                h = int(params.get("hour", 9))
                m = int(params.get("minute", 0))
                with WORLD_LOCK:
                    WORLD.clock.set_time(hour=h, minute=m)
                    WORLD._update_weather_and_traffic()
                    new_data = WORLD.step()
                    LAST_TELEMETRY = new_data
                update_telemetry_cache(new_data)
                _push_sse(new_data)
                res = {"status": "ok", "time": f"{h:02d}:{m:02d}"}
            elif cmd == "direct_message":
                with WORLD_LOCK:
                    res = WORLD.direct_message_citizen(params.get("persona_id", "AARAV"), params.get("message", ""))
            self._send_json(res)
        elif parsed.path == "/api/step":
            with WORLD_LOCK:
                new_data = WORLD.step()
                LAST_TELEMETRY = new_data
            update_telemetry_cache(new_data)
            _push_sse(new_data)
            self._send_json(new_data)
        elif parsed.path == "/api/set_time":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            hour = int(body.get("hour", 9))
            minute = int(body.get("minute", 0))
            with WORLD_LOCK:
                WORLD.clock.set_time(hour=hour, minute=minute)
                WORLD._update_weather_and_traffic()
                new_data = WORLD.step()
                LAST_TELEMETRY = new_data
            update_telemetry_cache(new_data)
            _push_sse(new_data)
            self._send_json(new_data)
        elif parsed.path == "/api/toggle_auto":
            AUTO_RUNNING = not AUTO_RUNNING
            self._send_json({"status": "toggled", "auto_running": AUTO_RUNNING})
        elif parsed.path == "/api/broadcast":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            msg = body.get("message", "")
            with WORLD_LOCK:
                res = WORLD.broadcast_executive_directive(msg)
            self._send_json(res)
        elif parsed.path == "/api/place_voxel":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            zone = body.get("zone", "Manyata_Tech_Park")
            x = int(body.get("x", 10))
            y = int(body.get("y", 10))
            btype = body.get("block_type", "solar_panel")
            with WORLD_LOCK:
                res = WORLD.voxel_world.place_block("GOVERNOR", "Lalith (City Governor)", zone, x, y, btype, WORLD.tick_count)
            self._send_json(res)
        elif parsed.path == "/api/direct_message":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            pid = body.get("persona_id", "AARAV")
            msg = body.get("message", "")
            with WORLD_LOCK:
                res = WORLD.direct_message_citizen(pid, msg)
            self._send_json(res)
        elif parsed.path == "/api/macro_event":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            ev_type = body.get("event_type", "MONSOON_FLOOD")
            with WORLD_LOCK:
                res = WORLD.trigger_macro_event(ev_type)
            self._send_json(res)
        elif parsed.path == "/api/campaign/launch":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            with WORLD_LOCK:
                res = WORLD.consumer_marketing.create_or_update_campaign(
                    campaign_id=body.get("id", f"CAMP-{int(time.time()*1000)%100000}"),
                    name=body.get("name", "New Innovation"),
                    tagline=body.get("tagline", "High-performance solution"),
                    sector=body.get("sector", "TECH_DEV_TOOL"),
                    price_inr=float(body.get("price_inr", 1999.0)),
                    claimed_utility=float(body.get("claimed_utility", 8.0)),
                    actual_quality=float(body.get("actual_quality", 8.0)),
                    variant=body.get("variant", "A"),
                    channel=body.get("channel", "ALL"),
                    target_audience=body.get("target_audience", "ALL"),
                    tick=WORLD.tick_count
                )
            self._send_json(res)
        elif parsed.path == "/api/campaign/ab_test":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            with WORLD_LOCK:
                camp_a, camp_b = WORLD.consumer_marketing.create_ab_test(
                    base_id=body.get("base_id", f"AB-{int(time.time()*1000)%100000}"),
                    name=body.get("name", "Product Test"),
                    sector=body.get("sector", "TECH_DEV_TOOL"),
                    variant_a_tagline=body.get("variant_a_tagline", "Technical & Benchmark-Driven"),
                    variant_a_price=float(body.get("variant_a_price", 1999.0)),
                    variant_b_tagline=body.get("variant_b_tagline", "Supercharge your workflow! 10x speed"),
                    variant_b_price=float(body.get("variant_b_price", 2999.0)),
                    claimed_utility=float(body.get("claimed_utility", 8.5)),
                    actual_quality=float(body.get("actual_quality", 8.5)),
                    tick=WORLD.tick_count
                )
            self._send_json({"variant_a": camp_a, "variant_b": camp_b})
        elif parsed.path == "/api/campaign/focus_group":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            q = body.get("question", "Would you buy this product?")
            camp_id = body.get("campaign_id")
            cohort = body.get("cohort_filter", "ALL")
            with WORLD_LOCK:
                fg_res = WORLD.consumer_marketing.run_synthetic_focus_group(
                    question=q,
                    campaign_id=camp_id,
                    cohort_filter=cohort,
                    citizens=WORLD.personas,
                    tick=WORLD.tick_count
                )
                target_p = fg_res.get("summary", {}).get("target_product", "New Bangalore Innovation")
                target_price = fg_res.get("summary", {}).get("target_price_inr", 2499.0)
                sector = fg_res.get("summary", {}).get("detected_sector", "TECH_DEV_TOOL")
                fg_res["visual_creative"] = WORLD.creative_engine.generate_ad_creative(target_p, q, target_price, sector)
            self._send_json(fg_res)
        elif parsed.path == "/api/citizen/call":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            c_name = body.get("citizen_name", "Aarav Sharma")
            u_msg = body.get("message", "How is your architecture scaling today?")
            with WORLD_LOCK:
                cit = None
                for p in WORLD.personas.values():
                    if p.name.lower() == c_name.lower():
                        cit = p
                        break
                if not cit:
                    cit = list(WORLD.personas.values())[0]

                task_desc = getattr(cit, 'current_task', getattr(cit, 'last_action', 'Deep Architecture & Systems Execution'))
                spoken = f"Namaskara! This is {cit.name}, {cit.role}. I am currently at {cit.location} working on {task_desc}. My wallet balance is ₹{cit.wallet_inr:,.0f} and energy is {cit.energy:.0f}%. We are shipping at high velocity in Bengaluru today!"
                WORLD.vector_brain.store_memory(cit.id, cit.name, f"Governor phone call: {u_msg}", "PHONE_CALL", WORLD.tick_count)
            self._send_json({
                "status": "CONNECTED",
                "citizen": cit.name,
                "role": cit.role,
                "location": cit.location,
                "wallet_inr": cit.wallet_inr,
                "spoken_response": spoken
            })
        elif parsed.path == "/api/creative/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            p_name = body.get("product_name", "DevPulse AI")
            pitch = body.get("pitch", "High-performance developer tooling for Bangalore architects")
            price = float(body.get("price_inr", 2499.0))
            sector = body.get("sector", "TECH_DEV_TOOL")
            with WORLD_LOCK:
                ad = WORLD.creative_engine.generate_ad_creative(p_name, pitch, price, sector)
            self._send_json(ad)
        elif parsed.path == "/api/social/post":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            txt = body.get("text", "")
            with WORLD_LOCK:
                tweet = WORLD.social_os.post_user_tweet(txt)
            self._send_json(tweet)
        elif parsed.path == "/api/fauna/interact":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode()) if length else {}
            c_name = body.get("citizen_name", "Aarav Sharma")
            a_id = body.get("animal_id", "d1")
            act = body.get("action", "PET")
            with WORLD_LOCK:
                res = WORLD.fauna_engine.interact_with_fauna(c_name, a_id, act)
            self._send_json(res)
        else:
            self.send_error(404)

class MetropolisServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        """Suppress broken pipe and connection reset logs when browser tabs disconnect."""
        ex_type, _, _ = sys.exc_info()
        if ex_type in (BrokenPipeError, ConnectionResetError):
            return
        super().handle_error(request, client_address)

def run_server(port: int = 9090, host: str = "0.0.0.0", interval: float = 3.5, auto: bool = True):
    global CURRENT_SERVER, TICK_INTERVAL_SEC, AUTO_RUNNING
    TICK_INTERVAL_SEC = interval
    AUTO_RUNNING = auto
    if not acquire_pid_lock(PID_FILE):
        print("✗ [Bengaluru OS] Aborting startup to prevent duplicate process collision.")
        sys.exit(1)

    atexit.register(release_pid_lock, PID_FILE)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    bg_thread = threading.Thread(target=background_autonomous_runner, daemon=True)
    bg_thread.start()

    server = MetropolisServer((host, port), WorldHandler)
    CURRENT_SERVER = server
    print(f"⚡ Bengaluru Living Metropolis OS Dashboard live at: http://{host}:{port} (PID: {os.getpid()})")
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        server.server_close()
        release_pid_lock(PID_FILE)
        print("✓ [Bengaluru OS] Server socket closed cleanly.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bengaluru Living Agent Metropolis OS Runner")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 9090)), help="HTTP Port (default: 9090)")
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "0.0.0.0"), help="Host address (default: 0.0.0.0)")
    parser.add_argument("--interval", type=float, default=float(os.environ.get("TICK_INTERVAL_SEC", 3.5)), help="Tick interval in seconds (default: 3.5)")
    parser.add_argument("--no-auto", action="store_true", help="Start with autonomous runner paused")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host, interval=args.interval, auto=not args.no_auto)
