You are a senior full-stack engineer with strong AWS ECS experience. Analyze the Node BFF + Vite React web app service in this repo to determine why the container does not return HTTP 200 as expected when deployed behind an ALB.

CONTEXT
- Deployed on ECS Fargate behind ALB host-based routing.
- Target group may be HTTPS:8080 (or similar).
- Symptom: no 200 from the service when called through ALB/DNS. Possibly 404/502/503.
- The Node service serves the built React assets and exposes API endpoints that proxy to an internal Python FastAPI service.

WHAT TO CHECK (MUST)
1) Container/server binding:
   - Ensure Node listens on 0.0.0.0 (not localhost)
   - Verify PORT env var handling and mapping to containerPort in task definition
   - Confirm process startup command and working directory
2) Routes and health endpoint:
   - Confirm /health exists and returns 200
   - Confirm ALB health check path matches
   - Confirm SPA routing fallback (serving index.html) and static asset paths
3) TLS:
   - If target group is HTTPS→container, confirm Node is actually serving HTTPS on that port (certs?) OR recommend switching TG to HTTP and terminate TLS at ALB only
4) Reverse proxy to FastAPI:
   - Ensure BFF uses internal DNS/service discovery and correct scheme/port
   - Timeouts, retries, and error handling (avoid leaking internals)
5) Build + runtime:
   - Confirm Vite build output is included in container image
   - Confirm Node serves correct directory
   - Dockerfile multi-stage best practices; avoid dev server in production
6) Logging:
   - Ensure request logs exist (at least access logs) to confirm traffic hits container
   - Identify where CloudWatch logs are configured

DELIVERABLE
- Root cause candidates ranked by likelihood with repo evidence.
- Exact code changes for:
   - adding a /health endpoint
   - binding to 0.0.0.0 and correct PORT
   - serving SPA with fallback
- Exact container/Dockerfile changes if needed.
- A minimal “curl tests” list to run locally and inside the task (including container-level curl).
- A short checklist to validate ALB → container → node route.

CONSTRAINTS
- Keep it maintainable and production-oriented.
- Prefer simple Node setup (Express/Fastify) and minimal changes.