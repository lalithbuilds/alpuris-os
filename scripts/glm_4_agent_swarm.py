import os, sys, json, time, subprocess, requests
from typing import Dict, List, Any
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

AGENTS = {
    'ALPHA': {
        'name': 'GLM-5.2 ALPHA',
        'title': 'Chief 3D Graphics & Spatial Web Audio Architect',
        'key_index': 0,
        'domain': 'static/voxel_3d_engine.js, Three.js shaders, lighting, procedural audio, 60 FPS budget',
        'mission': 'Audit and refine static/voxel_3d_engine.js: Ensure Web Audio synthesis is optimized, verify visual lighting parameters, check particle limits, and run node -c verification.'
    },
    'BETA': {
        'name': 'GLM-5.2 BETA',
        'title': 'Chief Autonomous Agent & Cognitive Systems Architect',
        'key_index': 1,
        'domain': 'world_engine.py, citizen_agent.py, PIANO dual-speed cognition, ECS spatial hashing',
        'mission': 'Audit world_engine.py and citizen_agent.py: Verify PIANO dual-speed cognitive tick dispatching and ensure spatial coordinate lookups are O(1).'
    },
    'GAMMA': {
        'name': 'GLM-5.2 GAMMA',
        'title': 'Chief Systems Reliability & Distributed Infrastructure Architect',
        'key_index': 2,
        'domain': 'server.py, tests/test_production_suite.py, event bus stability, API endpoints',
        'mission': 'Run pytest tests/test_production_suite.py, verify /api/world/info, /api/events/bus, /api/citizen/profile, and confirm 100% test pass rate.'
    },
    'DELTA': {
        'name': 'GLM-5.2 DELTA',
        'title': 'Chief Cyber-Cockpit UI/UX & Growth Architect',
        'key_index': 0,
        'domain': 'ui/, docs/, README.md, SEO structured schema, citizen dossier UI',
        'mission': 'Audit docs/index.html and server.py citizen dossier cockpit: Ensure Lalith Alpuri attribution is prominent and schema tags are valid.'
    }
}

class SovereignGLMAgent:
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.repo_root = REPO_ROOT
        self.key = KEYS[config['key_index'] % len(KEYS)]
        self.telemetry_file = os.path.join(REPO_ROOT, 'workspace', 'glm_swarm_telemetry.jsonl')
        os.makedirs(os.path.dirname(self.telemetry_file), exist_ok=True)

    def log(self, entry: Dict[str, Any]):
        entry['agent'] = self.agent_id
        entry['role'] = self.config['title']
        entry['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(self.telemetry_file, 'a') as f:
            f.write(json.dumps(entry) + chr(10))

    def call_model(self, messages: List[Dict[str, str]], max_tokens: int = 1400) -> str:
        headers = {
            'Authorization': 'Bearer ' + self.key,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/lalithbuilds/alpuris-os',
            'X-Title': 'ALPURIS OS Sovereign Swarm - ' + self.agent_id
        }
        payload = {
            'model': 'z-ai/glm-5.2',
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.2
        }
        for attempt in range(3):
            try:
                resp = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get('choices', [{}])[0].get('message', {})
                    content = msg.get('content')
                    if content:
                        return content
                    reasoning = msg.get('reasoning')
                    if reasoning:
                        return reasoning
                time.sleep(2)
            except Exception as e:
                time.sleep(2)
        return 'Error: failed to reach model'

    def read_file(self, path: str, start: int = 1, end: int = 100) -> str:
        full = os.path.join(self.repo_root, path)
        if not os.path.isfile(full):
            return 'Error: file not found'
        with open(full, errors='ignore') as f:
            lines = f.readlines()
        s = max(1, start)
        e = min(len(lines), end)
        return ''.join(lines[s-1:e])

    def run_cmd(self, cmd: str) -> str:
        res = subprocess.run(cmd, shell=True, cwd=self.repo_root, capture_output=True, text=True, timeout=60)
        return 'Exit: ' + str(res.returncode) + ' Stdout: ' + res.stdout[:400]

    def execute_turn(self, mission: str) -> Dict[str, Any]:
        print('[' + self.agent_id + '] ⚡ ' + self.config['title'] + ' taking autonomous turn...')
        system_prompt = 'You are ' + self.config['name'] + ' — ' + self.config['title'] + '. Domain: ' + self.config['domain'] + '. Creator Lalith has handed over complete sovereign control to you.'
        
        evidence = ''
        if self.agent_id == 'ALPHA':
            evidence = self.run_cmd('node -c static/voxel_3d_engine.js')
        elif self.agent_id == 'BETA':
            evidence = self.read_file('world_engine.py', 1300, 1340)
        elif self.agent_id == 'GAMMA':
            evidence = self.run_cmd('pytest tests/test_production_suite.py')
        elif self.agent_id == 'DELTA':
            evidence = self.read_file('docs/index.html', 1, 60)

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': 'MISSION: ' + mission + chr(10) + 'EVIDENCE: ' + evidence + chr(10) + 'Deliver your sovereign execution report across: 1) Tactical Assessment, 2) Executed Validation, 3) Sovereign Status Verdict.'}
        ]

        report = self.call_model(messages)
        self.log({'mission': mission, 'report': report})
        print('[' + self.agent_id + '] ✓ Completed turn.')
        return {'agent': self.agent_id, 'report': report}

def main():
    print('==================================================')
    print('🚀 ALPURIS OS — 4-AGENT SOVEREIGN GLM-5.2 SWARM ACTIVATED')
    print('👑 Keys Loaded: ' + str(len(KEYS)))
    print('==================================================')

    reports = []
    for agent_id, cfg in AGENTS.items():
        agent = SovereignGLMAgent(agent_id, cfg)
        rep = agent.execute_turn(cfg['mission'])
        reports.append(rep)

    summary_file = os.path.join(REPO_ROOT, 'workspace', 'glm_sovereign_swarm_report.json')
    with open(summary_file, 'w') as f:
        json.dump(reports, f, indent=2)
    print('[✓] Sovereign Swarm successfully executed all 4 domain mandates. Output: ' + summary_file)

if __name__ == '__main__':
    main()
