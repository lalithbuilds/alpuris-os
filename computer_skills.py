"""
Computer Skills Interface: Direct Integration with Docker X11 Virtual Desktop
Equips every persona with real OS execution powers (terminal, browser, mouse, screen).
"""

import os
import subprocess
import time
from typing import Dict, Any, Tuple

CONTAINER_NAME = "claude-computer-use"

class ComputerInterface:
    def __init__(self, container_name: str = CONTAINER_NAME):
        self.container_name = container_name
        self._ensure_container_alive()

    def _ensure_container_alive(self) -> bool:
        try:
            res = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", self.container_name],
                capture_output=True, text=True, timeout=3
            )
            return res.stdout.strip() == "true"
        except Exception:
            return False

    def execute_bash(self, command: str) -> Tuple[int, str]:
        """Runs a bash command inside the persona's virtual computer."""
        try:
            res = subprocess.run(
                ["docker", "exec", self.container_name, "bash", "-c", command],
                capture_output=True, text=True, timeout=10
            )
            out = res.stdout if res.returncode == 0 else res.stderr
            return res.returncode, out.strip()
        except subprocess.TimeoutExpired:
            return -1, "Execution timed out"
        except Exception as e:
            return -2, str(e)

    def launch_browser(self, url: str) -> str:
        """Launches Firefox on the virtual X11 screen (DISPLAY=:1)."""
        cmd = f"DISPLAY=:1 firefox-esr '{url}' &"
        code, out = self.execute_bash(cmd)
        return f"Browser launched to {url}" if code == 0 else f"Failed: {out}"

    def mouse_click(self, x: int, y: int, button: int = 1) -> str:
        """Moves mouse and clicks on the virtual display."""
        cmd = f"DISPLAY=:1 xdotool mousemove {x} {y} click {button}"
        code, out = self.execute_bash(cmd)
        return f"Mouse clicked at ({x}, {y})" if code == 0 else f"Failed: {out}"

    def type_keystrokes(self, text: str) -> str:
        """Types text into the active desktop window."""
        escaped = text.replace("'", "'\\''")
        cmd = f"DISPLAY=:1 xdotool type --delay 45 '{escaped}'"
        code, out = self.execute_bash(cmd)
        return "Typed text" if code == 0 else f"Failed: {out}"

    def capture_screenshot(self, host_output_path: str = "/tmp/world_live_view.png") -> bool:
        """Captures the live virtual desktop and copies it to the host."""
        container_tmp = "/tmp/screen_grab.png"
        code, _ = self.execute_bash(f"DISPLAY=:1 scrot {container_tmp}")
        if code != 0:
            return False
        try:
            subprocess.run(
                ["docker", "cp", f"{self.container_name}:{container_tmp}", host_output_path],
                check=True, timeout=5
            )
            return True
        except Exception:
            return False
