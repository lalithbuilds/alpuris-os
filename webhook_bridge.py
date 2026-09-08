"""
Webhook Dispatcher & External Push Notification Bridge
Bengaluru Living Metropolis OS
- Dispatches rich alert notifications to external webhooks (Discord / Local endpoints)
- Non-blocking asynchronous worker queue prevents stalling simulator ticks
- Bounded memory log prevents heap exhaustion during 24/7 runtime
- Triggers on: Silk Board Gridlock, Startup Bankruptcies, Focus Group Commercial Failures
"""

import urllib.request
import json
import time
import threading
import queue
from typing import Dict, Any, List, Optional

class WebhookBridge:
    def __init__(self, webhook_url: Optional[str] = None, max_history: int = 100):
        self.webhook_url = webhook_url
        self.notification_log: List[Dict[str, Any]] = []
        self._max_history = max_history
        self._queue: queue.Queue = queue.Queue(maxsize=100)
        self._worker_thread = threading.Thread(target=self._dispatch_worker, daemon=True)
        self._worker_thread.start()

    def set_webhook_url(self, url: str):
        self.webhook_url = url

    def _dispatch_worker(self):
        """Dedicated background worker thread for non-blocking HTTP dispatch."""
        while True:
            try:
                item = self._queue.get()
                url, discord_payload = item
                req = urllib.request.Request(
                    url,
                    data=json.dumps(discord_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "MetropolisOS/1.0"}
                )
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    pass
            except Exception:
                pass
            finally:
                self._queue.task_done()

    def dispatch_alert(self, title: str, description: str, alert_type: str = "INFO", fields: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Dispatch a structured notification without blocking simulation ticks."""
        payload = {
            "title": f"⚡ [BENGALURU OS] {title}",
            "description": description,
            "alert_type": alert_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fields": fields or []
        }
        self.notification_log.append(payload)
        if len(self.notification_log) > self._max_history:
            self.notification_log = self.notification_log[-self._max_history:]

        # Asynchronous non-blocking dispatch
        if self.webhook_url and self.webhook_url.startswith("http"):
            discord_payload = {
                "username": "Bengaluru Metropolis Governor",
                "embeds": [{
                    "title": payload["title"],
                    "description": payload["description"],
                    "color": 15158332 if alert_type == "ALERT" else 3066993,
                    "fields": fields or []
                }]
            }
            try:
                self._queue.put_nowait((self.webhook_url, discord_payload))
            except queue.Full:
                pass

        return payload

    def get_recent_alerts(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.notification_log[-limit:]
