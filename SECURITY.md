# Security Policy

## Supported Versions

The `main` branch is the supported development line for ALPURIS OS. Security fixes are applied to `main` first.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately by email to the maintainer listed in the project profile, or by opening a private GitHub security advisory when available.

Do not publish exploit details in a public issue before the maintainer has had a chance to review and patch the problem.

## Runtime Safety Notes

ALPURIS OS includes a sandboxed execution layer and local workspace APIs. Treat any deployment as a local development system unless you have explicitly added authentication, network isolation, and resource limits for your environment.

Before exposing the server beyond localhost, review:

- workspace read/write boundaries
- command and script execution paths
- environment variables and local credentials
- logs and generated files for sensitive content
- reverse proxy authentication and TLS settings

The default development server is not intended to be internet-facing without additional hardening.
