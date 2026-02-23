You are a senior AWS ECS Fargate + Terraform platform engineer. I already have an ECS cluster deployed (do NOT create a new cluster, VPC, or ALB/NLB from scratch unless required by existing modules). I need to ADD two new services to the existing cluster:

1) UI/BFF Service (Node) – serves Vite React build + BFF routes
    - Publicly reachable via existing ALB using host-based routing
    - Must expose GET /health returning 200
    - Must bind to 0.0.0.0 and use PORT env var
    - Prefer: TLS terminates at ALB, container is HTTP internally
    - NOTE: Our org has Sentinel policies: standalone aws_lb_target_group may be rejected if not created via an approved module. Reuse existing approved modules/patterns in this repo.

2) Internal API Service (Python FastAPI)
    - Internal-only (no public ALB rule)
    - Reachable only from the UI/BFF service over the VPC
    - Must expose GET /health returning 200
    - Use Cloud Map (ECS Service Discovery) if already used in repo; otherwise propose the simplest internal DNS approach that matches existing patterns.

GOALS
- Add Terraform code to create: ECS task definitions, ECS services, IAM roles (task + execution) as needed, security groups, log groups, service discovery, and ALB listener rule + target group for UI/BFF.
- Reuse existing cluster, subnets, security baseline, and load balancer(s). Integrate with the existing ALB listener (HTTPS:443) and existing host-based routing approach.
- Produce minimal diffs that pass Sentinel: if target groups/listener rules must be created through an approved module, implement the new target group and rule using that module and outputs (do NOT create standalone resources if policy rejects them).

INPUTS YOU MUST DISCOVER FROM THIS REPO (do not ask me; infer from code)
- Existing cluster name/ARN outputs
- Existing ALB listener ARN for HTTPS:443 and how rules are added today
- Existing “approved modules” used for target groups/listener rules (search module "nlb" or any LB module)
- Existing VPC/subnet IDs passed into ECS services
- Existing logging conventions (CloudWatch log group naming)
- Existing IAM role conventions for ECS tasks
- Existing naming/tagging conventions
- Existing Sentinel-compliant patterns (where TGs are defined, how rules are created)

REQUIRED IMPLEMENTATION DETAILS
A) UI/BFF (Node)
- Task definition with container port (choose repo convention; likely 8080)
- Env vars: PORT, NODE_ENV, FASTAPI_BASE_URL (internal DNS), etc.
- CloudWatch logs configured
- ECS Service wired to ALB via compliant target group output
- ALB listener rule: Host header = <ui_host> forwards to UI target group
- Security groups:
    - ALB SG → UI SG inbound on UI port
    - UI SG egress to FastAPI SG on FastAPI port

B) FastAPI
- Task definition with container port (likely 8000)
- Env vars and secrets wiring consistent with repo
- CloudWatch logs configured
- ECS Service internal-only (no ALB attachment)
- Service discovery name (e.g., fastapi.<namespace>) or internal-only method that matches existing patterns
- Security group:
    - FastAPI SG inbound only from UI SG on FastAPI port

DELIVERABLES
1) Diff-style Terraform patches:
    - New files/modules to add the two services
    - Variable additions (variables.tf) and outputs (outputs.tf) if required
    - Any updates needed to existing ALB rule module inputs
2) A short “how to deploy” sequence:
    - terraform fmt/validate/plan/apply steps
    - any prerequisites (ECR images, env vars)
3) A verification plan with exact commands:
    - curl https://<ui_host>/health should return 200
    - curl https://<ui_host>/ should serve index.html
    - curl https://<ui_host>/<spa-route> should return index.html (SPA fallback)
    - From within UI task: curl http://<fastapi_dns>:<port>/health returns 200

CONSTRAINTS / GUARDRAILS
- Do not create a new ECS cluster.
- Do not introduce Docker Compose for production.
- Avoid breaking existing infra; keep changes minimal.
- Must conform to Sentinel policies and existing approved modules.
- Prefer HTTP from ALB to task unless compliance forces HTTPS; if compliance forces HTTPS, document exactly how certs are provided to the task and how health checks work.

START
1) Locate existing ECS cluster + ALB module usage.
2) Implement UI/BFF service additions following existing patterns.
3) Implement internal FastAPI service additions following existing patterns.
4) Ensure security group rules and service discovery are correct.
5) Output complete patches and verification steps.