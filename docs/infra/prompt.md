You are a senior Terraform + AWS platform engineer. Our Sentinel policy rejects standalone `aws_lb_target_group` resources that use HTTP; it allows compliant target groups when created through an approved remote module (e.g., our load balancer/NLB module).

TASK
Refactor this repo so the ALB target group (and if required, the listener rule) for the BFF webapp is created through the approved module rather than as a standalone `aws_lb_target_group` resource.

CONTEXT
- Existing ALB: alb
- Listener: HTTPS:443
- Current routing is host-based (Host header → forward to TG)
- ECS service uses Fargate with target_type = ip
- Current failing resource: `aws_lb_target_group.agm_webapp_ecs_tg` because it uses protocol="HTTP" and health_check.protocol="HTTP" and is not part of any approved module.
- Goal end state: ALB terminates TLS; target group can be HTTP to container (preferred) while passing Sentinel via the approved module.

REQUIREMENTS
1) Identify the approved module used in this repo for load balancer / target group resources (search for `module "nlb"` or similar shared modules).
2) Determine how that module expects target group definitions (variables/inputs) and how it outputs target group ARNs.
3) Move TG creation (and listener rule if necessary) into the module usage pattern.
4) Update the ECS service to reference the module’s `target_group_arn` output.
5) Preserve:
    - Host-based routing
    - target_type = "ip"
    - health check path = "/health"
6) Provide a minimal diff:
    - Remove/replace `aws_lb_target_group.agm_webapp_ecs_tg`
    - Add module config and outputs
    - Adjust `aws_lb_listener_rule` / ECS service accordingly
7) Explain any new variables/inputs needed and where to define them (variables.tf/locals).

DELIVERABLE
- Exact Terraform code changes (diff-style) and file locations.
- If the approved module does NOT support ALB target groups, propose the smallest change:
  a) extend module to support ALB TGs, or
  b) add an approved “alb_target_group” module wrapper, or
  c) request a Sentinel policy exemption with a precise justification.

CONSTRAINTS
- Do not suggest moving to EKS or changing the overall architecture.
- Keep changes minimal and compliant with Sentinel.
- Prefer HTTP to container unless compliance forces HTTPS.