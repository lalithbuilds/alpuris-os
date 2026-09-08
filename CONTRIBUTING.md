# Contributing to Bengaluru Living Agent Metropolis OS

Thank you for your interest in contributing to the Bengaluru Living Agent Metropolis OS!

## Architectural Principles
1. **Zero Bloat**: Favor standard library simplicity over unneeded third-party frameworks.
2. **Deterministic Economics**: Any financial transaction must balance through `life_and_economy_engine.py`.
3. **Security Gate**: Never commit credentials, `.env` files, or un-sanitized API responses.
4. **Resiliency**: The 24/7 background runner must never crash on network timeouts or disconnected SSE clients.

## Development Workflow
1. Fork the repository and create a feature branch (`git checkout -b feat/your-feature`).
2. Run the environment setup: `./scripts/setup.sh`.
3. Ensure all tests pass: `./scripts/test.sh`.
4. Commit your changes with conventional commit messages (`feat:`, `fix:`, `docs:`).
5. Open a Pull Request against `main`.
