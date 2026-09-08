#!/usr/bin/env python3
"""
GLM-5.2 Autonomous Engineer & Architect Harness
Gives z-ai/glm-5.2 complete autonomous access to read, write, edit, test, and iterate on codebase files.
Uses multi-key rotation across OpenRouter keys.
"""

import os
import sys
import json
import re
import time
import subprocess
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(REPO_ROOT, ".env"))

def get_api_keys() -> List[str]:
    raw = os.getenv("OPENROUTER_KEYS", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    single = os.getenv("OPENROUTER_API_KEY", "")
    if single and single not in keys:
        keys.append(single)
    # Deduplicate and filter dummy keys
    keys = [k for k in dict.fromkeys(keys) if not k.endswith("key1") and not k.endswith("key2")]
    if not keys:
        raise RuntimeError("No valid OpenRouter API keys found in .env")
    return keys

class GLMAutonomousEngineer:
    def __init__(self, model: str = "z-ai/glm-5.2", repo_root: str = REPO_ROOT):
        self.repo_root = repo_root
        self.model = model
        self.keys = get_api_keys()
        self.key_idx = 0
        self.log_file = os.path.join(repo_root, "workspace", "glm_audit_log.jsonl")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        print(f"🚀 GLM-5.2 Autonomous Engineer initialized with {len(self.keys)} OpenRouter keys.")
        print(f"📁 Working Directory: {self.repo_root}")

    def _next_key(self) -> str:
        key = self.keys[self.key_idx % len(self.keys)]
        self.key_idx += 1
        return key

    def _log(self, entry: Dict[str, Any]):
        entry["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def call_glm(self, messages: List[Dict[str, str]], max_tokens: int = 1500) -> str:
        for attempt in range(len(self.keys) * 3):
            key = self._next_key()
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/lalithbuilds/metropolis",
                "X-Title": "Metropolis GLM-5.2 Autonomous Harness"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            try:
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0]["message"].get("content")
                        if content:
                            return content
                        reasoning = choices[0]["message"].get("reasoning")
                        print(f"⚠️ GLM returned empty content (reasoning len: {len(reasoning or '')}), retrying...")
                elif resp.status_code in (402, 429, 502, 503, 504):
                    print(f"⚠️ Key {key[:10]}... returned status {resp.status_code}, backing off 2s and rotating...")
                    time.sleep(2)
                else:
                    print(f"❌ API Error {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"⚠️ Network error with key {key[:10]}...: {e}, rotating...")
                time.sleep(2)
        raise RuntimeError("All OpenRouter keys exhausted or failed.")

    # ---------------- TOOLS ----------------
    def read_file(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        full_path = os.path.normpath(os.path.join(self.repo_root, path))
        if not full_path.startswith(self.repo_root):
            return f"Error: Access denied outside repo: {path}"
        if not os.path.isfile(full_path):
            return f"Error: File not found: {path}"
        try:
            with open(full_path, "r", errors="ignore") as f:
                lines = f.readlines()
            total = len(lines)
            s = max(1, start_line or 1)
            e = min(total, end_line or min(total, s + 60))
            if e - s > 75:
                e = s + 75
            selected = lines[s - 1:e]
            output = [f"File: {path} (Lines {s}-{e} of {total})"]
            for idx, line in enumerate(selected, start=s):
                output.append(f"{idx:4d} | {line.rstrip()}")
            if e < (end_line or total):
                output.append(f"... [Truncated. Next chunk begins at line {e+1}]")
            return "\n".join(output)
        except Exception as e:
            return f"Error reading file {path}: {e}"

    def write_file(self, path: str, content: str) -> str:
        full_path = os.path.normpath(os.path.join(self.repo_root, path))
        if not full_path.startswith(self.repo_root):
            return f"Error: Access denied outside repo: {path}"
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully written {len(content)} characters to {path}"
        except Exception as e:
            return f"Error writing file {path}: {e}"

    def edit_file(self, path: str, target_snippet: str, replacement_snippet: str) -> str:
        full_path = os.path.normpath(os.path.join(self.repo_root, path))
        if not full_path.startswith(self.repo_root):
            return f"Error: Access denied outside repo: {path}"
        if not os.path.isfile(full_path):
            return f"Error: File not found: {path}"
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                original = f.read()

            if target_snippet in original:
                updated = original.replace(target_snippet, replacement_snippet, 1)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(updated)
                return f"Successfully applied exact edit to {path}"

            # Fallback: line-trimmed matching
            target_lines = [l.strip() for l in target_snippet.strip().splitlines() if l.strip()]
            orig_lines = original.splitlines()
            found_start = -1
            match_len = len(target_lines)

            for i in range(len(orig_lines) - match_len + 1):
                window = [orig_lines[i + j].strip() for j in range(match_len)]
                if window == target_lines:
                    found_start = i
                    break

            if found_start != -1:
                # Replace the window with replacement_snippet
                new_orig_lines = orig_lines[:found_start] + replacement_snippet.splitlines() + orig_lines[found_start + match_len:]
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_orig_lines) + "\n")
                return f"Successfully applied fuzzy-trimmed edit to {path} (line {found_start+1})"

            return f"Error: target_snippet not found in {path}. Please verify exact lines."
        except Exception as e:
            return f"Error editing file {path}: {e}"

    def run_command(self, command: str) -> str:
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=90
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            return f"Exit Code: {res.returncode}\nSTDOUT:\n{out[:4000]}\nSTDERR:\n{err[:2000]}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 90 seconds."
        except Exception as e:
            return f"Error running command: {e}"

    def list_files(self, directory: str = ".") -> str:
        full_path = os.path.normpath(os.path.join(self.repo_root, directory))
        if not full_path.startswith(self.repo_root):
            return f"Error: Access denied: {directory}"
        try:
            entries = []
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if d not in [".git", "vendor", "__pycache__", ".pytest_cache", "node_modules"]]
                for f in files:
                    p = os.path.relpath(os.path.join(root, f), self.repo_root)
                    size = os.path.getsize(os.path.join(root, f))
                    entries.append(f"{p} ({size} bytes)")
            return "\n".join(entries[:100])
        except Exception as e:
            return f"Error listing files: {e}"

    def execute_tool(self, call: Dict[str, Any]) -> str:
        tool_name = call.get("tool")
        if tool_name == "read_file":
            return self.read_file(call.get("path", ""), call.get("start_line"), call.get("end_line"))
        elif tool_name == "write_file":
            return self.write_file(call.get("path", ""), call.get("content", ""))
        elif tool_name == "edit_file":
            return self.edit_file(call.get("path", ""), call.get("target_snippet", ""), call.get("replacement_snippet", ""))
        elif tool_name == "run_command":
            return self.run_command(call.get("command", ""))
        elif tool_name == "list_files":
            return self.list_files(call.get("directory", "."))
        elif tool_name == "finish_task":
            return f"MISSION ACCOMPLISHED: {call.get('summary', 'Done')}"
        else:
            return f"Unknown tool: {tool_name}"

    def parse_action(self, response_text: str) -> Optional[Dict[str, Any]]:
        # Check if response contains a json code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        # Check if entire response is json
        try:
            return json.loads(response_text.strip())
        except Exception:
            pass
        # Search for first JSON-like object
        match = re.search(r"(\{[\s\S]*\"tool\"[\s\S]*\})", response_text)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        return None

    def run_mission(self, mission_goal: str, max_steps: int = 15) -> Dict[str, Any]:
        print(f"\n==================================================")
        print(f"🎯 STARTING GLM-5.2 MISSION:")
        print(f"{mission_goal}")
        print(f"==================================================\n")

        system_prompt = (
            "You are GLM-5.2, an expert autonomous systems engineer with full access to the codebase.\n"
            "You have direct access to read, write, edit files and execute shell commands in this repository.\n\n"
            "AVAILABLE TOOLS (Respond with ONLY a single JSON object):\n"
            "1. Read file:\n"
            '   {"tool": "read_file", "path": "relative/path.ext", "start_line": 1, "end_line": 100}\n'
            "2. Edit file (surgical patch):\n"
            '   {"tool": "edit_file", "path": "relative/path.ext", "target_snippet": "<exact text to replace>", "replacement_snippet": "<new text>"}\n'
            "3. Write file (create or overwrite entire file):\n"
            '   {"tool": "write_file", "path": "relative/path.ext", "content": "<full file content>"}\n'
            "4. Run shell command:\n"
            '   {"tool": "run_command", "command": "pytest ... / node -c ..."}\n'
            "5. List files in directory:\n"
            '   {"tool": "list_files", "directory": "."}\n'
            "6. Finish task:\n"
            '   {"tool": "finish_task", "summary": "<description of completed work>"}\n\n'
            "RULES:\n"
            "- Always read existing code before editing to guarantee exact string matches.\n"
            "- After modifying JavaScript, run `node -c static/voxel_3d_engine.js`.\n"
            "- After modifying Python, run `pytest tests/test_production_suite.py`.\n"
            "- Never produce speculative or placeholder code. Provide fully functioning, robust implementations.\n"
            "- Output JSON ONLY."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"MISSION GOAL:\n{mission_goal}\n\nPlease begin by inspecting the relevant files."}
        ]

        history = []
        for step in range(1, max_steps + 1):
            print(f"--- [Step {step}/{max_steps}] Calling GLM-5.2 ---")
            raw_response = self.call_glm(messages)
            action = self.parse_action(raw_response)

            if not action:
                print(f"⚠️ Failed to parse JSON tool action from GLM-5.2:\n{raw_response[:300]}")
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": "Error: Your response must be a valid JSON object specifying a tool call. Example: {\"tool\": \"read_file\", \"path\": \"...\", \"start_line\": 1, \"end_line\": 50}"})
                continue

            tool_name = action.get("tool")
            print(f"🛠️ Tool Action: {tool_name} -> {action.get('path') or action.get('command') or ''}")

            if tool_name == "finish_task":
                summary = action.get("summary", "Mission completed.")
                print(f"\n🎉 MISSION COMPLETED BY GLM-5.2:\n{summary}\n")
                self._log({"mission": mission_goal, "status": "completed", "summary": summary, "steps": step})
                return {"status": "success", "summary": summary, "steps": step}

            obs = self.execute_tool(action)
            obs_preview = obs[:300] + "..." if len(obs) > 300 else obs
            print(f"👁️ Observation: {obs_preview}\n")

            self._log({"step": step, "action": action, "observation_preview": obs_preview})

            messages.append({"role": "assistant", "content": json.dumps(action)})
            # Keep prompt compact to avoid OpenRouter credit reservation caps
            if len(obs) > 2500:
                obs_to_pass = obs[:2200] + "\n... [Observation truncated to preserve context budget]"
            else:
                obs_to_pass = obs
            messages.append({"role": "user", "content": f"OBSERVATION:\n{obs_to_pass}\n\nWhat is your next tool call?"})
            if len(messages) > 6:
                messages = [messages[0], messages[1]] + messages[-4:]

        return {"status": "max_steps_reached", "summary": "Reached maximum allotted steps."}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GLM-5.2 Autonomous Engineer Harness")
    parser.add_argument("--mission", type=str, default="", help="Custom mission goal for GLM-5.2")
    parser.add_argument("--steps", type=int, default=15, help="Maximum steps allowed for mission")
    args = parser.parse_args()

    runner = GLMAutonomousEngineer()
    if args.mission:
        goal = args.mission
    else:
        goal = "Inspect static/voxel_3d_engine.js and report the total lines and key rendering loop structure."
    res = runner.run_mission(goal, max_steps=args.steps)
    print(json.dumps(res, indent=2))
