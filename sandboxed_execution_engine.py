"""
Sandboxed Execution & Real Code Runtime Engine
Bengaluru Living Metropolis OS
- Executes real python code tasks when tech citizens claim bounties on the P2P market
- AST Security Gate: Blocks dangerous imports (os, subprocess, socket), system calls, and eval/exec
- Process Group Isolation: Kills runaway processes and child forks without leaving zombie threads
- Resource Caps: Enforces strict wall-clock timeout and CPU limits
- Ephemeral Lifecycle: Unlinks temporary task files immediately to prevent disk exhaustion
- Memory Bounded: Retains capped telemetry buffer preventing heap leaks
"""

import os
import sys
import subprocess
import hashlib
import time
import ast
import signal
import resource
import collections
from typing import Dict, Any, List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SANDBOX_DIR = os.environ.get("ALPURIS_SANDBOX_DIR", os.path.join(PROJECT_ROOT, "sandbox"))
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Citizen scripts may only import a small computational stdlib.
# A denylist misses `import builtins`, `import pathlib`, and `from sys import modules`.
ALLOWED_MODULES = {
    "sys", "json", "math", "time", "statistics", "collections", "itertools",
    "functools", "re", "datetime", "decimal", "random", "string", "typing",
    "heapq", "bisect", "array", "numbers", "fractions", "copy", "pprint",
    "textwrap", "dataclasses", "enum", "abc", "contextlib", "operator",
}
FORBIDDEN_FUNCS = {
    "eval", "exec", "compile", "breakpoint", "__import__", "open",
    "getattr", "setattr", "delattr", "globals", "locals", "vars", "dir",
    "type", "object", "super", "help", "input", "memoryview",
}
FORBIDDEN_ATTRS = {
    "__subclasses__", "__globals__", "__code__", "__builtins__", "__class__",
    "__bases__", "__mro__", "__dict__", "__init__", "__new__", "__reduce__",
    "__reduce_ex__", "modules", "gi_frame", "f_globals", "f_builtins", "_getframe",
}
_CHILD_MEMORY_BYTES = 512 * 1024 * 1024


def _blocked_name(name: str) -> bool:
    return name in FORBIDDEN_FUNCS or name in FORBIDDEN_ATTRS or name.startswith("_")


def validate_citizen_ast(task_code: str) -> Tuple[bool, str]:
    """Strict AST security validation for citizen bounty scripts."""
    try:
        tree = ast.parse(task_code)
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"

    for node in ast.walk(tree):
        # 1. Allow only the computational stdlib. Everything else is blocked,
        # including builtins, pathlib, and io, which can open files.
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod not in ALLOWED_MODULES:
                    return False, f"Prohibited module import: '{alias.name}'"
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or node.level:
                return False, "Prohibited module import: relative import"
            mod = node.module.split(".")[0]
            if mod not in ALLOWED_MODULES:
                return False, f"Prohibited module import: '{node.module}'"
            for alias in node.names:
                imported = alias.name.split(".")[0]
                if alias.name == "*" or _blocked_name(imported):
                    return False, f"Prohibited module import: '{alias.name}'"

        # 2. Block prohibited function calls, including getattr/open aliases
        # that would otherwise slip past an attribute denylist.
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCS:
                return False, f"Prohibited built-in call: '{node.func.id}()'"
            elif isinstance(node.func, ast.Attribute) and _blocked_name(node.func.attr):
                return False, f"Prohibited introspection call: '{node.func.attr}()'"

        # 3. Block dangerous attribute access, including dunder traversal.
        elif isinstance(node, ast.Attribute):
            if _blocked_name(node.attr):
                return False, f"Prohibited attribute access: '{node.attr}'"

        # 4. Block loading a forbidden builtin into another name (`f = open`).
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and _blocked_name(node.id):
            return False, f"Prohibited built-in reference: '{node.id}'"

    return True, "VALIDATED"


class SandboxedExecutionEngine:
    def __init__(self, max_history: int = 100):
        self.execution_history: collections.deque = collections.deque(maxlen=max_history)
        self._sweep_stale_files()

    def _sweep_stale_files(self):
        """Clean up any orphan task files left from prior runs."""
        try:
            for f in os.listdir(SANDBOX_DIR):
                if f.startswith("task_") and f.endswith(".py"):
                    try:
                        os.unlink(os.path.join(SANDBOX_DIR, f))
                    except Exception:
                        pass
        except Exception:
            pass

    def execute_bounty_task(self, bounty_id: str, title: str, citizen_name: str, task_code: str) -> Dict[str, Any]:
        """Execute a citizen's code in the sandbox and record execution telemetry."""
        git_hash = hashlib.sha1(f"{task_code}:{time.time()}".encode()).hexdigest()[:7]

        # Phase 1: AST Pre-Execution Security Gate
        is_safe, sec_reason = validate_citizen_ast(task_code)
        if not is_safe:
            result = {
                "bounty_id": bounty_id,
                "title": title,
                "citizen_name": citizen_name,
                "script_file": "BLOCKED_BY_AST_SECURITY",
                "git_commit": f"commit {git_hash}",
                "status": "BLOCKED_SECURITY",
                "exit_code": 126,
                "elapsed_ms": 0.0,
                "stdout": "",
                "stderr": f"Security Violation: {sec_reason}",
                "timestamp": time.strftime("%H:%M:%S")
            }
            self.execution_history.append(result)
            return result

        # Phase 2: Ephemeral file generation
        file_hash = hashlib.sha256(f"{bounty_id}:{citizen_name}:{time.time()}".encode()).hexdigest()[:12]
        script_path = os.path.join(SANDBOX_DIR, f"task_{file_hash}.py")

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(task_code)

        start_time = time.time()
        exit_code = 1
        stdout = ""
        stderr = ""
        status = "FAILED"

        def _setup_child_process():
            # Create independent process group
            os.setsid()
            # Enforce CPU limit: 2s soft, 3s hard (kills infinite loops with SIGXCPU)
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (2, 3))
                resource.setrlimit(resource.RLIMIT_AS, (_CHILD_MEMORY_BYTES, _CHILD_MEMORY_BYTES))
            except Exception:
                pass

        child_env = {
            "PATH": "/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "LANG": os.environ.get("LANG", "C.UTF-8"),
        }

        try:
            proc = subprocess.Popen(
                [sys.executable, "-I", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=SANDBOX_DIR,
                env=child_env,
                preexec_fn=_setup_child_process
            )
            try:
                out, err = proc.communicate(timeout=3.0)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                exit_code = proc.returncode
                stdout = (out or "")[:1000]
                stderr = (err or "")[:1000]
                if exit_code == 0:
                    status = "PASSED"
                elif exit_code == -signal.SIGXCPU or exit_code == 137:
                    status = "CPU_LIMIT_EXCEEDED"
                    stderr = f"CPU time limit exceeded: {stderr}".strip()
                elif exit_code < 0:
                    status = f"KILLED_BY_SIGNAL_{abs(exit_code)}"
                else:
                    status = "FAILED"
            except subprocess.TimeoutExpired:
                elapsed_ms = 3000.0
                exit_code = 124
                # Terminate entire process group to eliminate zombie/orphan processes
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    proc.kill()
                proc.communicate()
                stdout = ""
                stderr = "Execution timed out (3.0s strict sandbox ceiling)"
                status = "TIMEOUT"

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            exit_code = 1
            stdout = ""
            stderr = str(e)
            status = "ERROR"
        finally:
            # Ephemeral disk hygiene: delete temporary file immediately
            if os.path.exists(script_path):
                try:
                    os.unlink(script_path)
                except Exception:
                    pass

        result = {
            "bounty_id": bounty_id,
            "title": title,
            "citizen_name": citizen_name,
            "script_file": f"sandbox/task_{file_hash}.py (ephemeral)",
            "git_commit": f"commit {git_hash}",
            "status": status,
            "exit_code": exit_code,
            "elapsed_ms": elapsed_ms,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.execution_history.append(result)
        return result

    def get_recent_runs(self, limit: int = 8) -> List[Dict[str, Any]]:
        runs = list(self.execution_history)
        return runs[-limit:]
