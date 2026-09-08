# 🏙️ Bengaluru Living Agent Metropolis OS

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Tests: 28 Passed](https://img.shields.io/badge/Tests-28%20Passed%20(100%25)-brightgreen.svg)](tests/test_production_suite.py)
[![WebGL: 60 FPS](https://img.shields.io/badge/WebGL-60%20FPS%20Locked-cyan.svg)](static/voxel_3d_engine.js)
[![Port: 9090](https://img.shields.io/badge/Port-9090%20Live-purple.svg)](http://localhost:9090)

**Bengaluru Living Agent Metropolis OS** is an autonomous, 24/7 generative multi-agent society simulating 100 heterogeneous AI citizens across 16 iconic sectors of Bengaluru (India's Silicon Valley). Powered by dual-speed cognitive architectures (System-1 Reflexive & System-2 Deliberative), real-time macro-economic SNA accounting, an Ornstein-Uhlenbeck stock market ticker, Vidhana Soudha municipal governance, and an interactive 3D WebGL voxel city cockpit.

---

## 📸 Visual Showcase

![Bengaluru Living Metropolis OS Cockpit](docs/assets/bengaluru_glm_upgraded_graphics.png)

*The real-time Cyber Cockpit with Autopolis telemetry cards, 3D Voxel skyline, moving Namma Metro trains, and live conversational feeds.*

![Manyata Tech Park Window Fly-Through](docs/assets/bengaluru_flythrough_verified.png)

*Seamless window fly-through camera descending from high-altitude orbit into Aarav Sharma's dual-monitor engineering workstation.*

![UB City Luxury Towers](docs/assets/bengaluru_ub_city_luxury_towers.png)

*UB City Luxury Towers featuring glowing neon wireframes, rooftop VIP helipads, and pulsating aviation obstruction beacons.*

---

## 🏛️ System Architecture

```
+-----------------------------------------------------------------------------------+
|               BENGALURU LIVING AGENT METROPOLIS OS (PORT 9090)                   |
+-----------------------------------------------------------------------------------+
                                         |
            +----------------------------+----------------------------+
            |                                                         |
+-----------------------+                                 +-----------------------+
|   BROWSER COCKPIT     |                                 |   EXECUTIVE CONSOLE   |
| - 3D Three.js Voxel   | <==== SSE Stream (/api/stream)  | - Governor Directives |
| - 2D HTML5 Canvas Map | <==== Gzip State (/api/state)   | - Focus Group Testing |
| - Autopolis HUD Cards | ===== Command API (/api/cmd) => | - Macro Emergency Ops |
+-----------------------+                                 +-----------------------+
            ^                                                         |
            |                                                         v
+-----------------------------------------------------------------------------------+
|                         METROPOLIS RUNTIME ENGINE                                 |
|                                                                                   |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |  Cognitive Core    |  |  Life & Economy    |  |  Civic Governance  |           |
|  |  - 100 Citizens    |  |  - INR Flow Ledger |  |  - Vidhana Soudha  |           |
|  |  - System 1/2 Dual |  |  - GDP = C+I+G+NX  |  |  - Bills 101-104   |           |
|  |  - SHA256 Caching  |  |  - OU Stock Market |  |  - Silk Board Grid |           |
|  +--------------------+  +--------------------+  +--------------------+           |
|                                                                                   |
|  +--------------------+  +--------------------+  +--------------------+           |
|  |  3D Voxel Spatial  |  |  Circadian Engine  |  |  Urban Fauna & TV  |           |
|  |  - 16 BLR Sectors  |  |  - Restorative Zzz |  |  - Stray Sheru/Cats|           |
|  |  - 3 Metro Lines   |  |  - Midday / Evening|  |  - 4 Live Channels |           |
|  |  - 60 FPS Scratch  |  |  - Shift Rotations |  |  - Namma Radio 91.1|           |
|  +--------------------+  +--------------------+  +--------------------+           |
+-----------------------------------------------------------------------------------+
```

---

## ⚡ Key Highlights & Features

### 1. 100 Autonomous AI Citizens & Guilds
- **Heterogeneous Personas**: Software Architects, Venture Capitalists, AI Researchers, Cafe Owners, Doctors, Students, and Darshini Cooks.
- **Dual-Speed Cognition**: System 1 instant heuristic reactions for casual chatter; System 2 deep LLM deliberation for architecture reviews and business negotiations.
- **Cognitive Response Caching**: SHA-256 state hashing with 5-minute TTL to prevent duplicate token costs and latency spikes.

### 2. Real-World Macro-Economy ($GDP = C + I + G + NX$)
- **SNA Compliance**: Tracks consumption ($C$), business investment ($I$), municipal spending ($G$), and tech exports ($NX$) through an atomic INR transaction flow ledger.
- **Financial Discipline**: Prevents negative citizen balances via strict `can_afford()` validation; withholds 10% TDS at source to continuously fund the municipal treasury.

### 3. BLR-TECH-30 Stock Market (Ornstein-Uhlenbeck)
- **Stochastic Equilibrium**: Discrete mean-reverting jump-diffusion process ($dS_t = \theta (\bar{S} - S_t) dt + \sigma S_t dW_t$) anchored to fundamental valuations.
- **8 Active Tickers**: INFX (Infosys), ZROD (Zerodha), SWGY (Swiggy), AURA (Aura AI), PEAK (PeakXV), YATR (Namma Yatri), QNTM (IISc Quantum), AERO (Kempegowda Aerospace).

### 4. 60 FPS WebGL 3D Voxel World
- **Three.js Engine**: ACESFilmicToneMapping, exposure calibration, and circadian exponential night mist (`THREE.FogExp2`).
- **Architectural Details**: VIP helipads with glowing yellow "H" markings on UB City, telecom spires on Manyata Tech Park, and pulsing red aviation obstruction beacons.
- **Zero-Allocation Rendering**: Pre-allocated scratch vectors (`_scratchV1`, `_scratchV2`, `_scratchLook`) completely eliminate garbage collection frame-drops.

### 5. High-Throughput Gzip & Server-Sent Events (SSE)
- **85% Wire Compression**: Pre-serialized binary cache serves `/api/state` compressed from 272 KB down to ~41 KB via `Content-Encoding: gzip`.
- **Sub-Millisecond SSE**: Low-latency push stream on `/api/stream` with `TCP_NODELAY` and automatic dead-subscriber eviction.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+ (Python Standard Library based)
- Modern Web Browser (Chrome, Firefox, Safari, Edge)

### Option A: Local Run (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/lalithbuilds/bengaluru-living-metropolis.git
cd bengaluru-living-metropolis

# 2. Automated environment setup
./scripts/setup.sh

# 3. Start the Metropolis Simulator (Port 9090)
./scripts/run.sh
```

Open **`http://localhost:9090`** in your browser to enter the Cyber Cockpit.

### Option B: Docker Deployment

```bash
# Build and run with Docker Compose
docker compose up -d

# View container logs
docker compose logs -f
```

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/state` | `GET` | Returns full telemetry snapshot (supports `Accept-Encoding: gzip`). |
| `/api/stream` | `GET` | Server-Sent Events (SSE) real-time stream pushed on every tick. |
| `/api/command` | `POST` | Unified executive command dispatcher (`broadcast`, `macro_event`, `step`, `toggle_auto`, `set_time`, `direct_message`). |
| `/api/campaign/focus_group` | `POST` | Executes a synthetic consumer focus group across filtered citizen cohorts. |
| `/api/zone_blocks` | `GET` | Returns voxel grid geometry for a specified Bengaluru zone. |
| `/api/workspace` | `GET` | Returns live markdown tabloid, architecture, and security workspace files. |

---

## 🧪 Production Test Suite

Run the full 28-suite production regression test:

```bash
./scripts/test.sh
# or via pytest directly:
python3 -m pytest tests/test_production_suite.py -v
```

```
============================== 28 passed in 10.59s ==============================
✓ Circadian Engine & Restorative Sleep (3/3 passed)
✓ Municipal Bills & Governance Execution (4/4 passed)
✓ Sandboxed Execution & Security Gate (5/5 passed)
✓ Cognitive Core Caching & Anti-Cascade (5/5 passed)
✓ WebGL Raycasting & Texture Disposal (4/4 passed)
✓ Concurrency, Resiliency & Broken-Pipe Eviction (4/4 passed)
✓ Ornstein-Uhlenbeck Stocks & SNA Flow Accounting (3/3 passed)
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Built by **Lalith** (*Ray Global Model*) in Nashik, Maharashtra.
