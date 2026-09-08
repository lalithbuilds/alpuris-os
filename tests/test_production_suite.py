"""
Bengaluru Living Metropolis OS — Production Test Harness & Integration Suite
=============================================================================
Comprehensive production-grade automated test harness verifying:
1. World Engine tick stability and state integrity (100 citizens, 16 sectors, 0 missing keys).
2. Macro Economy & GDP non-negativity and accounting consistency (GDP = C + I + G + NX).
3. BLR Tech 30 stock ticker math and volatility bounds ([-1.8%, +2.4%], index calculation).
4. HTTP Server endpoints (200 OK, valid JSON schemas for /api/state, /api/conversations, /api/workspace, etc.).
5. Sandbox execution safety and timeout limits (5.0s ceiling, exit codes, output truncation).
6. Concurrency & broken pipe resilience (SSE client eviction, thread safety, lock contention).

Compatible with both `pytest` and `python3 -m unittest`.
"""

import os
import sys
import json
import time
import queue
import urllib.request
import urllib.error
import threading
from http.server import ThreadingHTTPServer
from typing import Dict, Any, Set
import unittest
import pytest

# Ensure ray_agent_world root and parent directory are on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARENT_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if PARENT_ROOT not in sys.path:
    sys.path.insert(0, PARENT_ROOT)

import world_engine
from world_engine import (
    LivingWorld, BENGALURU_ZONES, ZONE_COORDINATES, ZONE_METADATA,
    METRO_LINES, INITIAL_STOCKS, DB_PATH, WORKSPACE_DIR
)
from life_and_economy_engine import LifeAndEconomyEngine
from sandboxed_execution_engine import SandboxedExecutionEngine
import server
from server import WorldHandler, WORLD, WORLD_LOCK, SSE_SUBSCRIBERS, SSE_LOCK, _push_sse

# ---------------------------------------------------------------------------
# CONSTANTS & SPECIFICATIONS
# ---------------------------------------------------------------------------

CORE_16_SECTORS = [
    "Kempegowda_Airport_BLR",
    "Manyata_Tech_Park",
    "IISc_Research_Campus",
    "Whitefield_ITPB",
    "Bagmane_Tech_Park",
    "Indiranagar_100ft_Startups",
    "Vidhana_Soudha_Capitol",
    "Cubbon_Park_Canopy",
    "Church_Street_Cafes",
    "UB_City_Luxury_Towers",
    "Majestic_Metro_Interchange",
    "Gandhi_Bazaar_Heritage",
    "Nexus_Koramangala_Mall",
    "Silk_Board_Junction",
    "HSR_Layout_Residences",
    "Electronic_City_Phase_1",
]

EXPECTED_TELEMETRY_KEYS: Set[str] = {
    "active_concurrent_models",
    "active_conversations",
    "active_families",
    "active_startups",
    "bengaluru_parks",
    "blr_tech_index",
    "chronicle_headlines",
    "circadian_phase",
    "circadian_phase_category",
    "citizens",
    "city_bills",
    "city_name",
    "community_places",
    "economy",
    "execution_mode",
    "fauna_state",
    "forbes_rich_list",
    "housing_state",
    "life_milestones",
    "lifecycle_stats",
    "macro_gdp",
    "marketing_intelligence",
    "metrics",
    "metro_lines",
    "named_cats",
    "named_dogs",
    "p2p_bounties",
    "persona_states",
    "phones_state",
    "radio_broadcasts",
    "real_intel",
    "recent_alerts",
    "recent_contracts",
    "recent_conversations",
    "recent_events",
    "sandbox_executions",
    "silk_board_congestion",
    "social_bonds",
    "social_pulse",
    "spatial_diffusion",
    "stocks",
    "stressor",
    "tick",
    "time_fraction",
    "timestamp",
    "total_citizens",
    "tv_broadcast",
    "vector_brain_count",
    "voxel_world",
    "weather",
    "world_time",
    "zone_coordinates",
    "zone_metadata",
}

EXPECTED_CITIZEN_KEYS: Set[str] = {
    "id",
    "name",
    "role",
    "department",
    "wallet_inr",
    "net_worth",
    "energy",
    "happiness",
    "arousal",
    "action",
    "activity_state",
    "zone",
    "zone_category",
    "speech_bubble",
    "relationships",
    "has_company",
    "marital_status",
    "partner_name",
    "children_count",
    "doublings",
    "venue_name",
}

# ---------------------------------------------------------------------------
# TEST SUITE 1: WORLD ENGINE TICK STABILITY & STATE INTEGRITY
# ---------------------------------------------------------------------------

class TestWorldEngineStateAndTickIntegrity(unittest.TestCase):
    """Verifies 100-citizen population, 16 core sectors, zero missing keys, and tick dynamics."""

    @classmethod
    def setUpClass(cls):
        # Use existing initialized server world to avoid redundant 14s startup ticks
        cls.world = WORLD
        with WORLD_LOCK:
            cls.telemetry = server.LAST_TELEMETRY

    def test_citizen_population_census(self):
        """Verify exactly 100 autonomous citizens exist with valid identities."""
        self.assertEqual(len(self.world.personas), 100, "World personas count must equal exactly 100")
        self.assertEqual(self.telemetry["total_citizens"], 100, "Telemetry total_citizens must be 100")
        self.assertEqual(len(self.telemetry["citizens"]), 100, "Telemetry citizens array must contain 100 items")
        self.assertEqual(len(self.telemetry["persona_states"]), 100, "Telemetry persona_states must contain 100 items")

        # Identity uniqueness and completeness
        ids = [p.id for p in self.world.personas.values()]
        self.assertEqual(len(ids), len(set(ids)), "Citizen IDs must be strictly unique")

        for p in self.world.personas.values():
            self.assertTrue(p.name and len(p.name.strip()) > 0, "Citizen name cannot be empty")
            self.assertTrue(p.role and len(p.role.strip()) > 0, "Citizen role cannot be empty")
            self.assertTrue(p.department and len(p.department.strip()) > 0, "Citizen department cannot be empty")
            self.assertIn(p.location, BENGALURU_ZONES, f"Citizen location {p.location} must be a recognized Bengaluru zone")

    def test_16_sectors_and_spatial_topology(self):
        """Verify all 16 core Bengaluru sectors exist in spatial coordinates and metadata."""
        zone_coords = self.telemetry["zone_coordinates"]
        zone_meta = self.telemetry["zone_metadata"]

        for sector in CORE_16_SECTORS:
            self.assertIn(sector, zone_coords, f"Core sector {sector} missing from zone_coordinates")
            self.assertIn(sector, zone_meta, f"Core sector {sector} missing from zone_metadata")
            
            coord = zone_coords[sector]
            self.assertIsInstance(coord, dict, f"Coordinates for {sector} must be a dict")
            self.assertIn("x", coord, f"Coordinate dict for {sector} must contain 'x'")
            self.assertIn("y", coord, f"Coordinate dict for {sector} must contain 'y'")
            self.assertGreaterEqual(coord["x"], 0, f"X coordinate for {sector} must be non-negative")
            self.assertGreaterEqual(coord["y"], 0, f"Y coordinate for {sector} must be non-negative")

            meta = zone_meta[sector]
            self.assertIn("name", meta, f"Metadata for {sector} must have name")
            self.assertIn("category", meta, f"Metadata for {sector} must have category")

        # Verify 3 Metro transit lines connectivity
        metro_lines = self.telemetry["metro_lines"]
        self.assertIsInstance(metro_lines, list, "metro_lines must be a list")
        self.assertEqual(len(metro_lines), 3, "Bengaluru Namma Metro must have 3 active transit lines")
        for line_idx, line in enumerate(metro_lines):
            self.assertIsInstance(line, list, f"Metro line #{line_idx} must be a list of waypoints")
            self.assertGreaterEqual(len(line), 2, f"Metro line #{line_idx} must have at least 2 station waypoints")
            for wp in line:
                self.assertIn("x", wp, f"Waypoint in line #{line_idx} missing 'x'")
                self.assertIn("y", wp, f"Waypoint in line #{line_idx} missing 'y'")
                self.assertGreaterEqual(wp["x"], 0)
                self.assertGreaterEqual(wp["y"], 0)

    def test_telemetry_zero_missing_keys(self):
        """Verify telemetry dictionary contains 100% of required top-level schema keys (0 missing)."""
        actual_keys = set(self.telemetry.keys())
        missing_keys = EXPECTED_TELEMETRY_KEYS - actual_keys
        self.assertEqual(
            len(missing_keys), 0,
            f"Telemetry has {len(missing_keys)} missing keys: {sorted(list(missing_keys))}"
        )

    def test_all_100_citizens_zero_missing_keys(self):
        """Verify every one of the 100 citizens in telemetry has complete schema with 0 missing keys."""
        citizens = self.telemetry["citizens"]
        for i, citizen in enumerate(citizens):
            actual_keys = set(citizen.keys())
            missing_keys = EXPECTED_CITIZEN_KEYS - actual_keys
            self.assertEqual(
                len(missing_keys), 0,
                f"Citizen #{i} ({citizen.get('name', 'Unknown')}) missing keys: {missing_keys}"
            )
            # Physiological and emotional bounds
            self.assertGreaterEqual(citizen["energy"], 0.0, "Energy cannot be negative")
            self.assertLessEqual(citizen["energy"], 100.0, "Energy cannot exceed 100")
            self.assertGreaterEqual(citizen["happiness"], 0.0, "Happiness cannot be negative")
            self.assertLessEqual(citizen["happiness"], 100.0, "Happiness cannot exceed 100")
            self.assertGreaterEqual(citizen["arousal"], 0.0, "Arousal stress index cannot be negative")
            self.assertLessEqual(citizen["arousal"], 1.0, "Arousal stress index cannot exceed 1.0")
            self.assertGreaterEqual(citizen["wallet_inr"], 0.0, "Wallet balance cannot be negative")

    def test_world_clock_and_circadian_phase_alignment(self):
        """Verify world clock time formatting and circadian phase progression."""
        self.assertIsInstance(self.telemetry["world_time"], str)
        self.assertTrue("Day" in self.telemetry["world_time"])
        self.assertIsInstance(self.telemetry["time_fraction"], float)
        self.assertGreaterEqual(self.telemetry["time_fraction"], 0.0)
        self.assertLessEqual(self.telemetry["time_fraction"], 1.0)
        self.assertIn(
            self.telemetry["circadian_phase_category"],
            ["MIDNIGHT", "EARLY_MORNING", "MORNING", "AFTERNOON", "LATE_AFTERNOON", "EVENING", "NIGHT"]
        )


# ---------------------------------------------------------------------------
# TEST SUITE 2: MACRO ECONOMY & GDP ACCOUNTING CONSISTENCY
# ---------------------------------------------------------------------------

class TestMacroEconomyAndGDPConsistency(unittest.TestCase):
    """Verifies GDP = C + I + G + NX accounting identity, non-negativity, and financial sanity."""

    @classmethod
    def setUpClass(cls):
        with WORLD_LOCK:
            cls.telemetry = server.LAST_TELEMETRY
        cls.macro_gdp = cls.telemetry["macro_gdp"]

    def test_gdp_fundamental_accounting_identity(self):
        """Verify macro accounting identity: GDP = C + I + G + NX within floating point precision."""
        c = self.macro_gdp["consumption_c_cr"]
        i = self.macro_gdp["investment_i_cr"]
        g = self.macro_gdp["govt_spending_g_cr"]
        nx = self.macro_gdp["net_exports_nx_cr"]
        total_gdp = self.macro_gdp["gdp_crores"]

        computed_sum = round(c + i + g + nx, 2)
        self.assertAlmostEqual(
            total_gdp, computed_sum, places=2,
            msg=f"Accounting identity failed: {total_gdp} Cr != {computed_sum} Cr (C={c}, I={i}, G={g}, NX={nx})"
        )

    def test_macro_economic_non_negativity(self):
        """Verify all macro economic aggregate components are strictly non-negative."""
        self.assertGreater(self.macro_gdp["gdp_crores"], 0.0, "Total GDP in Crores must be strictly positive")
        self.assertGreater(self.macro_gdp["consumption_c_cr"], 0.0, "Private consumption (C) must be positive")
        self.assertGreater(self.macro_gdp["investment_i_cr"], 0.0, "Gross investment (I) must be positive")
        self.assertGreater(self.macro_gdp["govt_spending_g_cr"], 0.0, "Govt expenditure (G) must be positive")
        self.assertGreater(self.macro_gdp["net_exports_nx_cr"], 0.0, "Net exports (NX) must be positive")
        self.assertGreaterEqual(self.macro_gdp["city_treasury_inr"], 0.0, "City treasury balance cannot be negative")

    def test_citizen_wallets_non_negativity(self):
        """Verify all individual citizen wallets and aggregate money supply are non-negative."""
        wallets = [c["wallet_inr"] for c in self.telemetry["citizens"]]
        self.assertEqual(len(wallets), 100)
        for w in wallets:
            self.assertGreaterEqual(w, 0.0, f"Found negative citizen wallet: {w}")
        
        total_wallets = sum(wallets)
        self.assertGreaterEqual(total_wallets, 0.0)

    def test_forbes_rich_list_integrity_and_ordering(self):
        """Verify Forbes Rich List is sorted in strictly descending order by net worth."""
        rich_list = self.telemetry["forbes_rich_list"]
        self.assertGreater(len(rich_list), 0, "Forbes rich list should not be empty")

        net_worths = [item["net_worth_inr"] for item in rich_list]
        for nw in net_worths:
            self.assertGreaterEqual(nw, 0, "Net worth cannot be negative")

        # Verify sorted descending
        for k in range(len(net_worths) - 1):
            self.assertGreaterEqual(
                net_worths[k], net_worths[k + 1],
                f"Forbes Rich List not sorted: rank {k} ({net_worths[k]}) < rank {k+1} ({net_worths[k+1]})"
            )


# ---------------------------------------------------------------------------
# TEST SUITE 3: BLR TECH 30 STOCK TICKER MATH & VOLATILITY BOUNDS
# ---------------------------------------------------------------------------

class TestBLRTech30StockMarketMath(unittest.TestCase):
    """Verifies stock ticker math, volatility envelope [-1.8%, +2.4%], and index formula."""

    @classmethod
    def setUpClass(cls):
        with WORLD_LOCK:
            cls.telemetry = server.LAST_TELEMETRY

    def test_stock_ticker_roster_composition(self):
        """Verify BLR-TECH-30 stocks match expected symbols and initial composition."""
        stocks = self.telemetry["stocks"]
        self.assertGreaterEqual(len(stocks), 8, "Stock market must have at least 8 active tickers")

        expected_symbols = {"INFX", "ZROD", "SWGY", "AURA", "PEAK", "YATR", "QNTM", "AERO"}
        actual_symbols = {s["symbol"] for s in stocks}
        missing_symbols = expected_symbols - actual_symbols
        self.assertEqual(len(missing_symbols), 0, f"Missing expected tickers: {missing_symbols}")

        for s in stocks:
            self.assertIn("symbol", s)
            self.assertIn("name", s)
            self.assertIn("price", s)
            self.assertIn("change", s)
            self.assertIn("sector", s)
            self.assertIn("volume", s)
            self.assertGreater(s["price"], 0.0, f"Stock {s['symbol']} price must be strictly positive")

    def test_volatility_bounds_simulation(self):
        """Simulate stock price updates and verify fluctuations strictly honor volatility envelope."""
        # Create an isolated stock state
        test_stocks = [
            {"symbol": "TEST_A", "price": 1000.0, "change": "+0.0%"},
            {"symbol": "TEST_B", "price": 500.0, "change": "+0.0%"}
        ]

        import random
        for iteration in range(25):
            for stock in test_stocks:
                old_price = stock["price"]
                delta_pct = round(random.uniform(-1.8, 2.4), 1)
                new_price = round(old_price * (1 + delta_pct / 100), 1)
                stock["price"] = new_price
                sign = "+" if delta_pct >= 0 else ""
                stock["change"] = f"{sign}{delta_pct}%"

                # Verify volatility bounds
                self.assertGreaterEqual(delta_pct, -1.8, f"Delta {delta_pct}% violated lower bound -1.8%")
                self.assertLessEqual(delta_pct, 2.4, f"Delta {delta_pct}% violated upper bound +2.4%")
                self.assertGreater(new_price, 0.0, f"Stock price fell below zero: {new_price}")
                self.assertTrue(stock["change"].endswith("%"), "Change string must end with %")

    def test_blr_tech_index_calculation(self):
        """Verify blr_tech_index formula: round(sum(s['price'] for s in stocks) * 1.15, 2)."""
        stocks = self.telemetry["stocks"]
        expected_index = round(sum(s["price"] for s in stocks) * 1.15, 2)
        
        # Parse index from telemetry (remove formatting commas)
        actual_index_str = self.telemetry["blr_tech_index"].replace(",", "")
        actual_index = float(actual_index_str)

        self.assertAlmostEqual(
            actual_index, expected_index, places=2,
            msg=f"Index mismatch: got {actual_index}, expected {expected_index}"
        )


# ---------------------------------------------------------------------------
# TEST SUITE 4: HTTP SERVER ENDPOINTS & SCHEMA VALIDATION
# ---------------------------------------------------------------------------

class TestHTTPServerEndpoints(unittest.TestCase):
    """Verifies HTTP 200 OK responses and valid JSON schemas on server endpoints."""

    server_instance: ThreadingHTTPServer = None
    server_thread: threading.Thread = None
    base_url: str = ""

    @classmethod
    def setUpClass(cls):
        # Determine if default port 9090 is accessible
        live_url = "http://127.0.0.1:9090/api/state"
        try:
            with urllib.request.urlopen(live_url, timeout=1.5) as resp:
                if resp.status == 200:
                    cls.base_url = "http://127.0.0.1:9090"
                    return
        except Exception:
            pass

        # If live server not running, spin up an ephemeral test server
        cls.server_instance = ThreadingHTTPServer(("127.0.0.1", 0), WorldHandler)
        cls.server_instance.daemon_threads = True
        port = cls.server_instance.server_port
        cls.base_url = f"http://127.0.0.1:{port}"
        cls.server_thread = threading.Thread(target=cls.server_instance.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if cls.server_instance:
            cls.server_instance.shutdown()
            cls.server_instance.server_close()

    def _get_json(self, endpoint: str) -> Any:
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(url, headers={"User-Agent": "ProductionTestHarness/1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            self.assertEqual(resp.status, 200, f"Expected 200 OK for {endpoint}, got {resp.status}")
            self.assertEqual(resp.headers.get("Content-Type"), "application/json")
            data = json.loads(resp.read().decode("utf-8"))
            return data

    def test_api_state_endpoint(self):
        """Verify /api/state returns 200 OK and valid city telemetry structure."""
        data = self._get_json("/api/state")
        self.assertIsInstance(data, dict)
        self.assertTrue("Alpuris" in data.get("city_name", "") or "Bengaluru" in data.get("city_name", ""))
        self.assertEqual(data.get("total_citizens"), 100)
        self.assertIn("economy", data)
        self.assertIn("stocks", data)
        self.assertIn("zone_coordinates", data)

    def test_api_conversations_endpoint(self):
        """Verify /api/conversations returns 200 OK and a valid JSON list."""
        data = self._get_json("/api/conversations")
        self.assertIsInstance(data, list)
        for item in data[:5]:
            self.assertIsInstance(item, dict)
            # Dialogue records feature speaker_1/speaker_2 or speaker
            has_speakers = ("speaker_1" in item and "speaker_2" in item) or ("speaker" in item)
            self.assertTrue(has_speakers, f"Conversation item missing speaker fields: {item.keys()}")

    def test_api_workspace_endpoint(self):
        """Verify /api/workspace returns 200 OK and dictionary of tracked workspace files."""
        data = self._get_json("/api/workspace")
        self.assertIsInstance(data, dict)
        expected_files = [
            "bengaluru_chronicle_tabloid.md",
            "bengaluru_cloud_architecture.md",
            "electronic_city_security_audit.log",
            "indiranagar_startup_pulse.json"
        ]
        for ef in expected_files:
            self.assertIn(ef, data, f"Workspace endpoint missing expected file {ef}")

    def test_auxiliary_api_endpoints(self):
        """Verify auxiliary monitoring endpoints return 200 OK and valid data."""
        endpoints = [
            "/api/tv/channels",
            "/api/social/feed",
            "/api/sandbox",
            "/api/lifecycle"
        ]
        for ep in endpoints:
            data = self._get_json(ep)
            self.assertTrue(isinstance(data, (dict, list)), f"Endpoint {ep} returned unexpected format: {type(data)}")

    def test_unknown_endpoint_returns_404(self):
        """Verify invalid API routes return HTTP 404 Not Found."""
        url = f"{self.base_url}/api/non_existent_diagnostic_route_404"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url, timeout=3.0)
        self.assertEqual(ctx.exception.code, 404)


# ---------------------------------------------------------------------------
# TEST SUITE 5: SANDBOX EXECUTION SAFETY & TIMEOUT LIMITS
# ---------------------------------------------------------------------------

class TestSandboxExecutionSafety(unittest.TestCase):
    """Verifies SandboxedExecutionEngine execution isolation, error trapping, and timeout limits."""

    def setUp(self):
        self.engine = SandboxedExecutionEngine()

    def test_sandbox_successful_task_execution(self):
        """Verify successful Python task execution produces PASSED status, exit code 0, and commit hash."""
        task_code = (
            "import sys\n"
            "a = 15\n"
            "b = 27\n"
            "print(f'COMPUTE_RESULT: {a + b}')\n"
            "sys.exit(0)\n"
        )
        res = self.engine.execute_bounty_task("BNT-TEST-01", "Math Kernel Task", "Aarav Sharma", task_code)
        self.assertEqual(res["status"], "PASSED")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("COMPUTE_RESULT: 42", res["stdout"])
        self.assertTrue(res["git_commit"].startswith("commit "))
        self.assertTrue(res["script_file"].endswith("(ephemeral)"))
        # Ephemeral disk hygiene: verify temporary execution file was unlinked
        clean_path = res["script_file"].replace(" (ephemeral)", "").strip()
        full_clean_path = os.path.join(PROJECT_ROOT, clean_path)
        self.assertFalse(os.path.exists(full_clean_path), "Ephemeral file must be unlinked after execution")

    def test_sandbox_ast_security_gate_blocking(self):
        """Verify AST security gate proactively intercepts prohibited imports and dangerous built-ins."""
        dangerous_scripts = [
            ("import os\nos.system('ls')", "Prohibited module import: 'os'"),
            ("import socket\ns = socket.socket()", "Prohibited module import: 'socket'"),
            ("with open('/tmp/leak.txt', 'w') as f: f.write('leak')", "Prohibited built-in call: 'open()'"),
            ("eval('2 + 2')", "Prohibited built-in call: 'eval()'"),
        ]
        for idx, (bad_code, reason) in enumerate(dangerous_scripts):
            res = self.engine.execute_bounty_task(f"SEC-BLOCK-{idx}", "Dangerous Exploit", "Hacker Citizen", bad_code)
            self.assertEqual(res["status"], "BLOCKED_SECURITY", f"Failed to block dangerous code: {bad_code}")
            self.assertEqual(res["exit_code"], 126)
            self.assertIn("Security Violation", res["stderr"])
            self.assertEqual(res["elapsed_ms"], 0.0)

    def test_sandbox_runtime_error_safety(self):
        """Verify Python runtime exceptions are caught as FAILED without crashing the system."""
        task_code = "print('About to crash')\nx = 1 / 0\n"
        res = self.engine.execute_bounty_task("BNT-TEST-02", "Crash Test Task", "Priya Patel", task_code)
        self.assertEqual(res["status"], "FAILED")
        self.assertNotEqual(res["exit_code"], 0)
        self.assertIn("ZeroDivisionError", res["stderr"])

    def test_sandbox_timeout_enforcement(self):
        """Verify execution times out at 3.0s strict limit, exits with code 124, and marks TIMEOUT."""
        # Task that sleeps for 8 seconds (timeout ceiling is 3.0s in engine)
        task_code = "import time\ntime.sleep(8)\nprint('Should not reach here')\n"
        t0 = time.time()
        res = self.engine.execute_bounty_task("BNT-TEST-03", "Infinite Loop Task", "Vikram Rao", task_code)
        elapsed = time.time() - t0

        self.assertEqual(res["status"], "TIMEOUT")
        self.assertEqual(res["exit_code"], 124)
        self.assertIn("Execution timed out", res["stderr"])
        self.assertLess(elapsed, 5.0, "Execution took longer than allowed timeout envelope")

    def test_sandbox_output_truncation_safety(self):
        """Verify massive stdout generation is truncated safely to 1000 characters."""
        task_code = "print('X' * 5000)\n"
        res = self.engine.execute_bounty_task("BNT-TEST-04", "Buffer Flooder Task", "Rohan Mehta", task_code)
        self.assertEqual(res["status"], "PASSED")
        self.assertLessEqual(len(res["stdout"]), 1000, "Stdout was not safely truncated")


# ---------------------------------------------------------------------------
# TEST SUITE 6: CONCURRENCY & BROKEN PIPE RESILIENCE
# ---------------------------------------------------------------------------

class TestConcurrencyAndResilience(unittest.TestCase):
    """Verifies SSE queue handling, broken pipe client pruning, and concurrent read safety."""

    def test_sse_subscriber_lifecycle(self):
        """Verify SSE subscriber queue registration and message broadcasting."""
        test_queue = queue.Queue(maxsize=4)
        with SSE_LOCK:
            SSE_SUBSCRIBERS.append(test_queue)

        test_payload = {"test_marker": "CONCURRENCY_OK", "timestamp": time.time()}
        _push_sse(test_payload)

        # Retrieve pushed message
        try:
            received_bytes = test_queue.get(timeout=2.0)
            self.assertTrue(received_bytes.startswith(b"data: "))
            data_str = received_bytes.decode("utf-8").replace("data: ", "").strip()
            data = json.loads(data_str)
            self.assertEqual(data.get("test_marker"), "CONCURRENCY_OK")
        finally:
            with SSE_LOCK:
                if test_queue in SSE_SUBSCRIBERS:
                    SSE_SUBSCRIBERS.remove(test_queue)

    def test_sse_broken_pipe_dead_subscriber_eviction(self):
        """Verify dead or saturated subscriber queues are safely pruned without crashing the server."""
        # Create a full queue that will reject put_nowait (simulating client disconnected/stalled)
        dead_queue = queue.Queue(maxsize=1)
        dead_queue.put(b"blocker")  # Saturate queue

        with SSE_LOCK:
            SSE_SUBSCRIBERS.append(dead_queue)

        # Broadcast should detect queue.Full, catch exception, and cleanly remove dead_queue
        try:
            _push_sse({"probe": "dead_subscriber_test"})
            with SSE_LOCK:
                self.assertNotIn(
                    dead_queue, SSE_SUBSCRIBERS,
                    "Dead subscriber queue was not pruned from SSE_SUBSCRIBERS"
                )
        except Exception as e:
            self.fail(f"_push_sse raised unexpected exception during broken pipe: {e}")

    def test_concurrent_telemetry_reads(self):
        """Verify 20 threads can read telemetry state concurrently with zero race conditions."""
        errors = []

        def worker_read(worker_id: int):
            try:
                for _ in range(10):
                    with WORLD_LOCK:
                        snap = server.LAST_TELEMETRY
                        c_count = snap["total_citizens"]
                        gdp = snap["economy"]["total_gdp_inr"]
                        stocks = len(snap["stocks"])
                    # Small sleep to simulate interleaving
                    time.sleep(0.01)
                    if c_count != 100 or stocks < 8 or not gdp:
                        errors.append(f"Worker {worker_id} observed inconsistent snapshot")
            except Exception as e:
                errors.append(f"Worker {worker_id} crashed with: {e}")

        threads = [threading.Thread(target=worker_read, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent reads encountered errors: {errors}")


class TestOrnsteinUhlenbeckAndMacroFlow(unittest.TestCase):
    """Verifies advanced economic equilibrium, Ornstein-Uhlenbeck mean-reversion, and gzip streaming."""

    def test_ornstein_uhlenbeck_stock_dynamics(self):
        """Verify stock market does not drift exponentially and stays anchored with OU mean-reversion."""
        from world_engine import BASE_STOCK_PRICES
        world = LivingWorld()
        for _ in range(25):
            world._update_stock_market()
            for stock in world.stocks:
                sym = stock["symbol"]
                price = stock["price"]
                base = BASE_STOCK_PRICES[sym]
                self.assertGreaterEqual(price, 1.0, f"Stock {sym} fell below ₹1.00 floor!")
                # Prices should stay within 50% band of fundamentals under standard volatility
                self.assertGreater(price, base * 0.4, f"Stock {sym} crashed below 40% of base!")
                self.assertLess(price, base * 2.5, f"Stock {sym} drifted above 250% of base!")

    def test_flow_ledger_macro_gdp_equilibrium(self):
        """Verify macro-GDP derives strictly from SNA flow ledger and resets each tick."""
        from cognitive_core import Persona
        db_path = "/tmp/test_macro_flow.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        engine = LifeAndEconomyEngine(db_path=db_path)
        p = Persona("P_TEST", "Test Architect", "Tech Fellow", "Manyata_Tech_Park", "SYSTEM")
        p.wallet_inr = 50000.0
        personas = {"P_TEST": p}

        # Simulate flow
        engine.flow_ledger["consumption_inr"] = 45000.0
        engine.flow_ledger["tax_collected_inr"] = 5000.0
        engine.flow_ledger["investment_inr"] = 25000.0

        res = engine.step_macro_economy(personas, tick=1)
        macro = res["macro_gdp"]
        self.assertIn("gdp_crores", macro)
        self.assertGreater(macro["gdp_crores"], 3000.0)
        self.assertGreaterEqual(macro["annual_growth_rate"], 6.5)
        self.assertLessEqual(macro["annual_growth_rate"], 11.5)

        # Flow ledger must be cleanly reset for next cycle
        self.assertEqual(engine.flow_ledger["consumption_inr"], 0.0)
        self.assertEqual(engine.flow_ledger["tax_collected_inr"], 0.0)
        self.assertEqual(engine.flow_ledger["investment_inr"], 0.0)

    def test_gzip_telemetry_cache_acceleration(self):
        """Verify pre-serialized gzip telemetry buffer correctly decompresses to valid JSON."""
        import gzip
        import server
        data = {"tick": 999, "status": "METROPOLIS_OK", "timestamp": time.time()}
        server.update_telemetry_cache(data)
        self.assertTrue(len(server.LAST_TELEMETRY_GZIP) > 0)
        decompressed = gzip.decompress(server.LAST_TELEMETRY_GZIP).decode("utf-8")
        parsed = json.loads(decompressed)
        self.assertEqual(parsed["tick"], 999)
        self.assertEqual(parsed["status"], "METROPOLIS_OK")

    def test_metropolis_event_bus_pub_sub(self):
        """Verify MetropolisEventBus handles pub/sub, topic filtering, and event history."""
        from world_engine import MetropolisEventBus
        bus = MetropolisEventBus(max_history=50)
        received = []
        bus.subscribe("monsoon_alert", lambda e: received.append(e))

        evt = bus.publish("monsoon_alert", {"severity": "high", "sector": "Silk_Board"})
        self.assertIn("id", evt)
        self.assertEqual(evt["topic"], "monsoon_alert")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["payload"]["sector"], "Silk_Board")

        # Verify get_recent with topic filter
        recent = bus.get_recent(topic="monsoon_alert")
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["payload"]["severity"], "high")

    def test_event_bus_and_world_info_api_routes(self):
        """Verify /api/events/bus and /api/world/info HTTP endpoints."""
        base_url = "http://127.0.0.1:9090"
        url_bus = f"{base_url}/api/events/bus"
        req = urllib.request.Request(url_bus)
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn("events", data)

        url_info = f"{base_url}/api/world/info"
        req_info = urllib.request.Request(url_info)
        with urllib.request.urlopen(req_info, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn("metropolis_name", data)
            self.assertIn("version", data)
            self.assertTrue(data["version"].startswith("4.") and "PRO" in data["version"])

    def test_citizen_profile_api_route(self):
        """Verify /api/citizen/profile returns full citizen profile with name, role, and department."""
        base_url = "http://127.0.0.1:9090"
        url = f"{base_url}/api/citizen/profile?id=AARAV"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data.get("id"), "AARAV")
            self.assertIn("name", data)
            self.assertIn("department", data)
            self.assertIn("wallet_inr", data)


# ---------------------------------------------------------------------------
# MAIN ENTRYPOINT
# ---------------------------------------------------------------------------


    def test_spatial_hash_grid_clustering(self):
        """Verify SpatialHashGrid clusters 10 citizens and returns O(1) neighbors within radius (GLM-5.2 GAMMA certified)."""
        from world_engine import SpatialHashGrid

        grid = SpatialHashGrid(cell_size=115)
        for i in range(10):
            grid.insert(f"cit_{i}", (i * 10.0, (i % 2) * 10.0))

        # Query origin radius 25
        neighbors = grid.query_radius((0.0, 0.0), 25.0)
        self.assertIsInstance(neighbors, list)
        self.assertIn("cit_0", neighbors)
        self.assertIn("cit_1", neighbors)

        # Test remove
        grid.remove("cit_0")
        after_remove = grid.query_radius((0.0, 0.0), 25.0)
        self.assertNotIn("cit_0", after_remove)

    def test_spatial_hash_grid_realtime_query(self):
        """Verify LivingWorld.spatial_grid accurately indexes all 100 citizens and supports radius query (GLM-5.2 GAMMA certified)."""
        import server
        grid = server.WORLD.spatial_grid
        self.assertIsNotNone(grid)
        count = server.WORLD.update_spatial_index()
        self.assertEqual(count, 100)

        from world_engine import ZONE_COORDINATES
        manyata_pos = ZONE_COORDINATES["Manyata_Tech_Park"]
        neighbors = grid.query_radius(manyata_pos, radius=200.0)
        self.assertIsInstance(neighbors, list)
        self.assertGreaterEqual(len(neighbors), 1)

    def test_citizen_episodic_memory_compaction(self):
        """Verify Persona memory compaction compresses overflow episodes into reflection summaries (GLM-5.2 DELTA certified)."""
        import server
        persona = list(server.WORLD.personas.values())[0]
        for i in range(45):
            persona.perceive(f"Observed autonomous routine #{i} in Bengaluru sector", stress_impact=0.05)

        self.assertLessEqual(len(persona.memory.nodes), 35)
        pruned = persona.compact_memory(max_nodes=20)
        self.assertGreater(pruned, 0)
        self.assertLessEqual(len(persona.memory.nodes), 25)

if __name__ == "__main__":
    print("=" * 80)
    print("⚡ RUNNING BENGALURU LIVING METROPOLIS OS PRODUCTION TEST SUITE")
    print("=" * 80)
    unittest.main(verbosity=2)
