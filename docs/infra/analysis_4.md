You are a senior AWS ECS/Fargate + Terraform engineer. Your goal is to simplify this stack to the standard pattern:

CLIENT (HTTPS) → ALB (TLS terminated with ACM) → ECS Task (HTTP only) → Node BFF serves Vite build + APIs → Node calls internal FastAPI service over VPC.

CRITICAL OUTCOME
- Remove TLS termination from the Node container (no https.createServer in app).
- Ensure Terraform/infra matches: ALB HTTPS listener forwards to an HTTP target group on the container port.
- End state must return 200 for /health through the ALB hostname, and SPA routes must work.

WHAT TO DO
1) Repo scan and call graph
- Locate Node BFF server startup code (index.ts/server.ts).
- Identify the current listening port and whether TLS is started in the app.
- Locate Terraform resources/modules for:
    - ALB (aws_lb)
    - listener(s) (aws_lb_listener)
    - listener rules (aws_lb_listener_rule)
    - target groups (aws_lb_target_group)
    - ECS service/task definition (aws_ecs_service, task definition/container port mappings)
    - security groups for ALB and services
    - Route53 records (if present)
    - NLB components (if present) and whether NLB is actually in the request path

2) Code simplification (Node BFF)
- Refactor the BFF to HTTP-only:
    - app.listen(PORT, '0.0.0.0')
    - Remove all TLS_CERT/TLS_KEY logic and https.createServer branches
- Ensure these endpoints exist:
    - GET /health → 200 OK (no dependencies)
    - SPA static serving + fallback to index.html for unknown routes
- Ensure PORT comes from env var and matches ECS containerPort
- Add minimal request logging (method/path/status) so we can verify requests reach the container.

3) Terraform alignment (must match HTTP-only container)
- Update (or create) the BFF target group:
    - protocol = "HTTP"
    - port = <BFF container port>
    - target_type = "ip"
    - health_check { protocol = "HTTP" path = "/health" matcher = "200" }
- Ensure the ALB listener remains HTTPS:443 with ACM cert and forwards to the HTTP target group via listener rule.
- Verify security groups:
    - ALB SG inbound: 443 from allowed CIDRs
    - ALB SG egress: to BFF service SG on BFF port
    - BFF service SG inbound: from ALB SG on BFF port
    - BFF egress: to FastAPI service SG on FastAPI port (internal only)

4) Service-to-service networking (Node → FastAPI)
- Confirm FastAPI is internal-only (no public LB).
- Confirm Node calls FastAPI via:
    - Cloud Map service discovery DNS OR internal load balancer OR VPC DNS name
- Ensure SG rule allows Node SG → FastAPI SG on the FastAPI port.
- Keep FastAPI protocol as HTTP internally unless a hard requirement exists.

5) Provide the exact diffs and commands
   DELIVERABLES REQUIRED
   A) A clear “before vs after” diagram for traffic:
    - HTTPS at edge only, HTTP inside VPC to tasks.
      B) A Terraform diff-style patch:
    - Which resources change (listener, target group, health check, ecs service load_balancer block, SG rules)
    - Exact values (ports, protocols, paths)
      C) A code diff-style patch for Node BFF startup and health route + SPA fallback
      D) A verification plan with commands:
    - curl -v https://<host>/health
    - curl -v https://<host>/ (confirm index.html)
    - curl -v https://<host>/<some-spa-route> (confirm fallback)
    - From inside BFF task: curl http://<fastapi-dns>:<port>/health
      E) A “rollback plan” describing how to revert safely if needed.

CONSTRAINTS
- Do not propose a re-architecture (no EKS, no CloudFront migration, etc.).
- Keep existing host-based routing approach.
- Prefer minimal change set that reliably restores 200 responses.
- If NLB exists, do not remove it unless you can prove it is unused; focus on getting ALB→ECS working first.

START NOW
- Identify the current BFF target group protocol/port and ALB listener forwarding.
- Identify where Node starts TLS and remove it.
- Ensure Terraform and code agree on protocol/port and health check path.