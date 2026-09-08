#!/usr/bin/env python3
import os, sys, json, time, requests
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(REPO_ROOT, '.env'))

def get_keys() -> List[str]:
    raw = os.getenv('OPENROUTER_KEYS', '')
    keys = [k.strip() for k in raw.split(',') if k.strip() and not k.endswith('key1') and not k.endswith('key2')]
    if not keys:
        single = os.getenv('OPENROUTER_API_KEY', '')
        if single:
            keys = [single]
    return keys

KEYS = get_keys()

def call_openrouter(key: str, model: str, messages: List[Dict[str, str]], max_tokens: int = 1500) -> str:
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/lalithbuilds/metropolis',
        'X-Title': 'Metropolis GLM-5.2 4-POV Council'
    }
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': 0.25
    }
    try:
        resp = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            msg = data.get('choices', [{}])[0].get('message', {})
            content = msg.get('content')
            if content:
                return content
            reasoning = msg.get('reasoning')
            if reasoning:
                return reasoning
            return 'No content returned.'
        else:
            return f'Error {resp.status_code}: {resp.text[:200]}'
    except Exception as e:
        return f'Exception: {e}'

COUNCIL_MEMBERS = [
    {
        'id': 'ALPHA',
        'role': 'GLM-5.2 ALPHA — Chief 3D Graphics & Spatial Engine Architect',
        'key_index': 0,
        'perspective': 'You champion visual splendor, WebGL/Three.js rendering performance, volumetric lighting, dynamic procedural shaders, LOD chunk streaming, and zero-asset procedural Web Audio immersion. Your mandate is to make this visually stunning at 60 FPS.'
    },
    {
        'id': 'BETA',
        'role': 'GLM-5.2 BETA — Chief Autonomous Agent & Cognitive Systems Architect',
        'key_index': 1,
        'perspective': 'You champion true autonomous depth, PIANO dual-speed cognition, ECS spatial hashing for O(1) proximity interactions, emergent social dynamics, citizen memory synthesis, dynamic jobs/salaries, and organic market economies without hardcoded scripts.'
    },
    {
        'id': 'GAMMA',
        'role': 'GLM-5.2 GAMMA — Chief Systems Reliability & Distributed OS Architect',
        'key_index': 2,
        'perspective': 'You champion server throughput, determinism, SSE streaming stability, thread-safe event bus messaging, lock-free memory concurrency, rock-solid REST APIs, zero race conditions, and 100% production test coverage.'
    },
    {
        'id': 'DELTA',
        'role': 'GLM-5.2 DELTA — Chief Product Visionary & UI/UX Cyber-Harness Designer',
        'key_index': 0,
        'perspective': 'You champion world branding, universal lore, the cyberpunk glassmorphism UI cockpit, citizen dossiers, radio broadcast culture, civic governance voting, and viral open-source developer appeal. Your goal is a world so captivating people can watch and interact with it for hours.'
    }
]

def run_pov(member: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    key = KEYS[member['key_index'] % len(KEYS)]
    system_prompt = (
        f"You are {member['role']}.\n"
        f"Perspective: {member['perspective']}\n"
        "You are participating in the high-level Model Council with Ray Global Model (Headless Orchestrator) and Creator Lalith.\n"
        "Your mission: Plan and execute the rebuild of the Living Agent Metropolis OS into the undisputed GREATEST AUTONOMOUS AGENT WORLD EVER BUILT.\n"
        "Provide a direct, authoritative, and structured technical response. Answer all 4 points directly."
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt}
    ]
    print(f"[*] Launching {member['id']} ({member['role']})...")
    start = time.time()
    resp = call_openrouter(key, 'z-ai/glm-5.2', messages, max_tokens=1400)
    dur = round(time.time() - start, 2)
    print(f"[✓] {member['id']} responded in {dur}s.")
    return {
        'id': member['id'],
        'role': member['role'],
        'duration': dur,
        'response': resp
    }

def main():
    print(f"🚀 Initializing GLM-5.2 4-POV Model Council Symposium with {len(KEYS)} API keys...")
    
    prompt_phase1 = """COUNCIL DIRECTIVE FROM CREATOR LALITH & RAY GLOBAL MODEL:
We are rebuilding the Living Agent Metropolis OS into the undisputed best autonomous agent world ever created.
Current Baseline:
- 100 Citizens with PIANO dual-speed cognition, 23 city sectors, stock market, municipal voting, newsroom.
- 3,732-line Three.js Voxel Engine with day/night, monsoon lightning, vehicle headlights, ground halos, and holographic beacons.
- 31/31 production tests passing.

Please address the following 4 points from your distinct architectural POV:
1. CODEBASE CRITIQUE: What is the single biggest architectural limitation in our current stack that we must eliminate?
2. YOUR ULTRA-UPGRADE: What is the most game-changing, bleeding-edge feature you propose adding in your domain right now?
3. UNIVERSAL REBRAND NAME: What is your #1 recommended global name for this world (moving away from 'Bengaluru')?
4. REQUIREMENTS & BLOCKERS: Do you have any specific requirements, dependencies, or questions for Lalith before proceeding with code changes? If none, confirm READY TO PROCEED."""

    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_pov, m, prompt_phase1) for m in COUNCIL_MEMBERS]
        for f in as_completed(futures):
            results.append(f.result())

    order = {'ALPHA': 0, 'BETA': 1, 'GAMMA': 2, 'DELTA': 3}
    results.sort(key=lambda x: order.get(x['id'], 99))

    os.makedirs(os.path.join(REPO_ROOT, 'workspace'), exist_ok=True)
    symposium_out = os.path.join(REPO_ROOT, 'workspace', 'glm_5_2_symposium_results.json')
    with open(symposium_out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[✓] All 4 POVs recorded to {symposium_out}!")

if __name__ == '__main__':
    main()
