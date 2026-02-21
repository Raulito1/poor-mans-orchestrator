You are a senior backend engineer specializing in FastAPI and AWS ECS Fargate. Analyze this repo’s FastAPI service deployment and integration with a Node BFF in the same ECS cluster.

CONTEXT
- FastAPI runs as an internal microservice (not public), invoked by the Node BFF.
- Symptom in the overall system: webapp doesn’t return 200; could be due to BFF failing on FastAPI calls or health checks.
- Environment may include Snowflake auth (external browser locally) but deployed in ECS.

WHAT TO CHECK (MUST)
1) Uvicorn/Gunicorn configuration:
    - Must bind to 0.0.0.0 and correct port
    - Confirm command used in Dockerfile/task definition
    - Confirm workers/timeouts appropriate for ECS
2) Health endpoint:
    - Provide /health returning 200 (no dependencies)
    - If readiness differs, recommend /ready
3) Networking & service discovery:
    - How Node resolves FastAPI (Cloud Map, internal DNS, or direct service name)
    - Ports and security group rules (FastAPI inbound from Node SG only)
4) Dependencies & startup:
    - Environment variables and secrets (AWS SSM/Secrets Manager)
    - Snowflake connectivity from ECS (network egress via NAT, DNS, certs)
5) Observability:
    - CloudWatch logs; structured logging
    - FastAPI exception handling; avoid leaking internals

DELIVERABLE
- Ranked list of probable deployment issues with repo evidence.
- Exact fixes for:
    - correct uvicorn command
    - ports/env wiring
    - health endpoints
    - security group + service discovery assumptions
- A “verification plan” to validate service is reachable from Node task (curl from inside Node task to FastAPI).