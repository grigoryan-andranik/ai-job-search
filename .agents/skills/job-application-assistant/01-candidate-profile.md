---
framework_version: 1.1.1
---

# Candidate Profile

<!-- SETUP: Populated by /setup Path A on 2026-09-11 from documents/cv/andranik_grigoryan_my_cv.pdf
     and documents/linkedin/Profile.pdf, with cross-reference conflicts resolved by the candidate. -->

## Identity
- **Name:** Andranik Grigoryan
- **Location:** Yerevan, Armenia
- **Phone:** +374 44 343937
- **Email:** theandranikgrigoryan@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/andranik-grigoryan/
- **GitHub:** https://github.com/andranikasd
- **Status:** Employed - DevOps Engineer at CodedCloud (remote, since Jul 2025). Actively looking; 2-week notice period.
- **Constraints:** Fully remote only - on-site roles are a deal-breaker. Prefers Armenian companies; remote roles at foreign companies are fine if they hire in Armenia. Based in Yerevan (UTC+4).
- **Target level:** Senior. All titles held are "DevOps Engineer"; "Senior" is positioning for profile statements and headlines, never written into a job-title field.
- **Salary baseline:** 1,500,000 AMD/month or more, **net (in hand)** - confirmed by the candidate on 2026-09-11.

### Languages
<!-- Every language you can work in professionally, with your honest level. Used by the
Language Gate in 04-job-evaluation.md and by job-scraper/search-queries.md's query-language
generation. Omit any language you don't actually work in - an undeclared language is treated as
a hard no, not a gap to smooth over. -->

| Language | Level | Notes |
|----------|-------|-------|
| Armenian | Native | |
| Russian | Fluent | |
| English | Professional working proficiency | Self-rated on CV (LinkedIn-style bucket) |

## Education

| Degree | Period | Institution | Key Topics |
|--------|--------|-------------|------------|
| Bachelor's degree in Cybersecurity | 2022-2026 (completed) | National Polytechnic University of Armenia, Yerevan | Not provided |

Studied alongside full-time DevOps work (Goya CJSC, Codeex, CodedCloud).

## Professional Experience

**Experience-length claims:** CVs list experience from Feb 2022 only (see "Omitted from CVs" below), so profile statements and cover letters say **"4+ years"**, never "5+". The candidate chose this on 2026-09-11 so the claim matches the dates a recruiter can add up.

### DevOps Engineer - CodedCloud (Jul 2025 - Present)
Remote. CodedCloud is a B2B IT services / consulting company. Title is **DevOps Engineer**, not "DevOps Consultant" (an older CV said Consultant; the candidate corrected it).
- Migrated manually managed Fastly CDN configuration to Terraform + Terragrunt, eliminating click-ops and enabling repeatable multi-environment deployments.
- Designed a self-hosted observability stack (Grafana, Loki, Mimir, Tempo, OpenTelemetry) handling 400 GB/day of logs and metrics, replacing a paid SaaS tool and cutting its cost by 75%. (An older CV said "1 TB+/day" - wrong; corrected by the candidate on 2026-09-11. Never use 1 TB.)
- Built an automated release and delivery pipeline with Kargo for production bare-metal Kubernetes, cutting release time by half.
- Works day-to-day with development and product management teams on the live production environment.
- Handles on-call incidents and production releases, and runs root-cause analysis (RCA) and post-mortems after incidents (confirmed by the candidate 2026-09-11).
- Set up an observability stack on EKS from scratch, replacing CloudWatch across multiple environments and cutting monitoring spend by 50%. This is a separate project from the 400 GB/day SaaS-replacement stack above (confirmed by the candidate 2026-09-11).

### DevOps Engineer - Codeex (Oct 2024 - Jul 2025)
Yerevan, Armenia. Codeex is the same company as PowerDMARC (per the candidate); CVs show it as **Codeex**. An older CV listed this work as "PowerDMARC, 2022-2024" - those dates are wrong.
- Migrated 100% of manually provisioned infrastructure to Terraform + Terragrunt with Atlantis, full drift detection and audit-ready change control.
- Designed and built a custom DNS service on AWS handling 120M+ requests/day at <80 ms P99 latency, cutting third-party licensing costs. **The DNS service's internals are under NDA - never name its implementation in a CV, letter or interview answer.**
- Reduced monthly AWS infrastructure costs by 50% through right-sizing and Reserved Instance planning.
- Owned all infrastructure-related SOC-2 Type II requirements through a successful audit. (Wording chosen by the candidate on 2026-09-11. Never write "led the audit".)
- AWS services used in production: EC2, Auto Scaling groups, S3, RDS, Lambda, API Gateway, CloudFront, WAF, Route 53, ALB, NLB, Global Accelerator, SQS, SNS, SES.
- Supported 70+ AWS Lambda environments.
- Worked closely with the AWS (Amazon) team on RDS performance and cost optimisation.
- Upgraded Laravel services from PHP-FPM 8.2 to 8.3.

### DevOps Engineer - Goya CJSC (Feb 2022 - Oct 2024)
Yerevan, Armenia. **Led the DevOps team** in practice (a two-person DevOps team); formal title on CVs is DevOps Engineer (candidate's choice). Team leadership may be stated in bullets and interviews. An older CV said "DevOps Lead, 2020-2022" - both the title and the dates are superseded.
- Designed and delivered bare-metal, self-hosted Kubernetes cluster infrastructure and automation from zero to production.
- Built an internal developer platform (IDP) with zero-trust security (mTLS, RBAC, network policies) for all tenant workloads.
- Automated environment provisioning with Ansible playbooks, cutting new-environment setup from days to under 30 minutes.
- Ran 4 Kubernetes clusters hosting complete self-hosted development platforms: GitLab with runners, Harbor registry, ELK logging, monitoring, Longhorn storage and MinIO for S3-compatible object storage.
- Fully automated release cycle with GitOps (ArgoCD); new cluster nodes bootstrapped with Ansible.
- The whole platform ran fully functional in air-gapped environments.

### Freelance DevOps Engineer - Upwork startup client (May 2026 - Aug 2026)
Remote, via Upwork, alongside the CodedCloud role. The client is WireUP, but **CVs, cover letters and interviews say "Upwork startup client" - never name the client** (candidate's choice, 2026-09-11). Described by the candidate as a fast-growing startup platform.
- Configured the client's AWS development, staging and production environments.
- Set up the SDLC, monitoring, infrastructure as code and operational-excellence practices.
- Set up the client's AWS environment following the AWS Well-Architected Framework.

### Omitted from CVs
- **DevOps Engineer - Stone Valley LLC (Jun 2020 - Jul 2022)**, Yerevan. Listed on LinkedIn, left off CVs at the candidate's request. Do not reintroduce it without asking. LinkedIn still shows it, so a recruiter may raise it - the candidate should be ready to explain the Feb-Jul 2022 overlap with Goya.

## Independent Projects
<!-- Projects outside of employment: freelance, open source, personal -->
- **Marum**: Telegram loan ledger and repayment planner with an English/Armenian mini-app. Go engine and PostgreSQL with versioned migrations; infrastructure in Terraform on Cloudflare plus a Docker Compose VPS; self-hosted observability (Grafana, Loki, Tempo, Prometheus, OpenTelemetry Collector); 9 GitHub Actions workflows covering CI, separate dev and prod deployments, infrastructure, releases and secrets. Built with Claude Code as coding assistant. Version 2.0.4 is deployed to a development environment; there is no production environment, so never claim production users. *(GitHub - marumbot)*
- **Discord Alert Bot**: TypeScript incident-alert delivery service. Ingests Grafana webhooks and AWS SNS via SQS, posts deduplicated alerts to Discord with per-incident threads, an acknowledge / troubleshoot / resolve lifecycle and escalation; CI, CodeQL scanning, release workflows, tests and a Docker image. *(GitHub - DiscordAlertingBot)*
- **K8s Resource Monitor**: Go microservice that health-checks Kubernetes custom resources, Pods, Jobs, PVs and PVCs through the Kubernetes API, with an HTTP status/reset API, configurable check intervals and rate limiting to protect the API server. *(GitHub - K8s-Resource-Monitor)*

*Reviewed by /expand on 2026-09-11 and deliberately not added (candidate kept only high-value projects): podfiles, keycloak-integrated-operator-helm, keycloak-cheatsheets, homelab, alpine-iso-builder, listamParser, fintrack, ansible-pet. Forks and personal-config repos were skipped.*

## Technical Skills

### Programming
Levels self-rated by the candidate on 2026-09-11.
- **Go** (working), **Python** (working), **Node.js / TypeScript** (basic), Bash / shell scripting

### IaC & Cloud
- Terraform, Terragrunt, Atlantis, Ansible
- AWS (EKS, EC2, Auto Scaling groups, S3, RDS, Lambda, API Gateway, CloudFront, WAF, Route 53, ALB, NLB, Global Accelerator, SQS, SNS, SES), GCP, OVH Cloud
- CloudWatch: hands-on; replaced it with a self-hosted observability stack on EKS across multiple environments (CodedCloud, confirmed 2026-09-11)
- AWS Well-Architected Framework applied to a client's dev / staging / prod setup (Upwork startup client)

### Containers & Kubernetes
- Kubernetes, Docker, Helm, Kustomize
- GitOps and delivery: ArgoCD, Flux, Kargo
- Self-hosted platform components: Harbor (registry), Longhorn (storage), MinIO (S3-compatible object storage)
- Air-gapped Kubernetes platforms (Goya)

### CI/CD
- GitLab CI/CD (including self-hosted GitLab and runners), GitHub Actions, Jenkins

### Observability
- Prometheus, Grafana, Loki, Tempo, Mimir, Alertmanager, Thanos, OpenTelemetry (OTEL)
- ELK stack (Goya)

### Databases
- PostgreSQL (tuning, replication, WAL, query optimisation), ScyllaDB, Redis, InfluxDB

### Networking & OS
- Nginx, HAProxy, Linux (RHEL/Ubuntu), Bash / shell scripting

### Security & Compliance
- Zero-trust networking, mTLS, RBAC, network policies
- SOC-2 (owned the infrastructure side of a Type II audit at Codeex), AWS Partnership Programme

### Engineering practices and tools from public projects
Added by /expand on 2026-09-11; each backed by a public GitHub repo.
- AI-assisted development with **Claude Code** *(GitHub - marumbot)*
- Security automation in CI: CodeQL scanning, Dependabot dependency updates *(GitHub - DiscordAlertingBot, marumbot)*
- Kubernetes API tooling in Go *(GitHub - K8s-Resource-Monitor)*
- PostgreSQL schema migrations with goose *(GitHub - marumbot)*
- Cloudflare managed with Terraform *(GitHub - marumbot)*
- Keycloak single sign-on (OIDC, SAML), including Keycloak operators on Kubernetes and ArgoCD SSO *(GitHub - keycloak-integrated-operator-helm, keycloak-cheatsheets)*

## Certifications
- **AWS Certified Solutions Architect - Associate (SAA-C03)** - earned 2023, **expired 2026**
- **Certified Kubernetes Administrator (CKA)**, CNCF - earned 2023, **expired 2026**

**Rule:** never present either certification as current. No headline badges and no "(SAA certified)" / "(CKA)" labels next to skills. When listed at all, list them only under Certifications with dates, e.g. "AWS Certified Solutions Architect - Associate (2023, expired 2026)".

## Publications
- None.

## Awards
- None.

## References
- No references provided yet.

Available upon request.
