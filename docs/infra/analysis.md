You are a senior AWS/ECS platform engineer. Perform a production-grade analysis of this repository’s ECS Fargate + load balancer infrastructure and identify why a deployed service might not return HTTP 200.

CONTEXT
- Platform: AWS ECS on Fargate
- Ingress: Application Load Balancer (ALB) using host-based routing
- Current symptom: service/task is “running” and target may appear healthy, but hitting the hostname does not return expected 200 (often 404/502/503).
- I need exact root causes and precise fixes.

SCOPE
1) Terraform:
    - ALB: listeners, listener rules, certificates, default actions, host/path rules, priority, target groups, health checks
    - Target groups: protocol/port (HTTP vs HTTPS), health check protocol/path/matcher, deregistration delay
    - ECS services: load_balancer blocks, container_name/container_port, service discovery, desired count, deployment settings
    - Networking: VPC, subnets (public/private), NAT, routing tables, ALB scheme (internet-facing vs internal)
    - Security groups: ALB SG inbound/outbound rules, service SG inbound from ALB SG, service-to-service SG
    - IAM: task execution role, task role, permissions for logs/secrets/ssm
    - CloudWatch: log groups, retention, alarms (if defined)

2) Runtime AWS verification checklist (what to click/validate in console):
    - ECS service events, target group registered targets, ALB listener rule matching, DNS records/alias, certificate coverage
    - How to confirm if a request is hitting the intended rule and target group

DELIVERABLE
- A table of findings with: Severity (Blocker/High/Med/Low), Evidence (exact file/resource names), Root cause, Fix (exact Terraform changes).
- A “fast path” troubleshooting flow for 404 vs 502 vs 503 vs timeout, tailored to ALB+ECS.
- A final section: “Most likely causes for not getting 200 in this repo” with ranked probabilities and why.

CONSTRAINTS
- Do not propose re-architecting (no “move to EKS” etc.). Fix within ECS/ALB/Terraform.
- Be explicit: reference the Terraform resources and settings in this repo.

START HERE
1) Identify where Terraform defines ALB, listeners, listener rules, target groups, ECS services/tasks.
2) Trace the request path: DNS → ALB listener → rule match → target group → task ENI → container port → app route.
3) Confirm health check alignment (protocol/path/matcher) with the app.