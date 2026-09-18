---
framework_version: 1.0.0
---

# Interview Preparation Guide

<!-- SETUP: STAR examples are personalized by running /setup based on your actual experience -->

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome).

Keep answers to 1-2 minutes. Be specific. End with what you learned or would do differently.

## Ready-Made STAR Examples

No complete examples yet. Fill in the S/T/A/R details for the entries under "STAR Candidates (Complete Manually)" below, then move finished ones up here in this format:

```
### N. [Project name] ([skill demonstrated])
**S:** context   **T:** your responsibility   **A:** what you did   **R:** measurable outcome
**Use for:** "question type 1", "question type 2"
```

<!-- Add more STAR examples as needed. Aim for 4-6 covering different competencies. -->

## STAR Candidates (Complete Manually)

<!-- Added by /setup Path A from the CV. Fill in S/T/A/R from memory before using any of these in an interview. -->

### Self-hosted LGTM observability stack replacing a paid SaaS tool
**Source:** CV - DevOps Engineer, CodedCloud
**What happened:** Designed a self-hosted Grafana / Loki / Mimir / Tempo / OpenTelemetry stack handling 400 GB/day of logs and metrics, replacing a paid SaaS tool and cutting its cost by 75%.
**Why it matters:** "Tell me about a system you designed", build-vs-buy and cost decisions, observability / SRE depth
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Fastly CDN configuration moved from click-ops to Terraform + Terragrunt
**Source:** CV - DevOps Engineer, CodedCloud
**What happened:** Moved manually managed Fastly CDN config into Terraform + Terragrunt, enabling repeatable multi-environment deployments.
**Why it matters:** IaC migrations, eliminating toil, working in a client's existing setup (consulting)
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Kargo release pipeline on bare-metal Kubernetes
**Source:** CV - DevOps Engineer, CodedCloud
**What happened:** Built an automated release pipeline with Kargo on bare-metal Kubernetes, reducing deployment cycle time and human error.
**Why it matters:** CI/CD and GitOps design, release safety, "how do you reduce deployment risk"
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result: (find a number if you can - cycle time before/after, failed releases)

### 100% of infrastructure migrated to Terraform with drift detection
**Source:** CV - DevOps Engineer, Codeex
**What happened:** Migrated all manually provisioned infrastructure to Terraform IaC with drift detection and audit-ready change control.
**Why it matters:** large migrations without downtime, change control, compliance readiness
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Self-hosted DNS service at 120M+ requests/day
**Source:** CV - DevOps Engineer, Codeex
**What happened:** Designed a custom self-hosted DNS service handling 120M+ requests/day at <80 ms P99, cutting third-party licensing costs.
**Why it matters:** high-load system design, latency / SLO work, build-vs-buy
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### 50% AWS cost reduction
**Source:** CV - DevOps Engineer, Codeex
**What happened:** Cut monthly AWS infrastructure costs by 50% through right-sizing and Reserved Instance planning.
**Why it matters:** FinOps / cost ownership, business impact, "tell me about a measurable result"
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### SOC-2 Type II audit
**Source:** CV - DevOps Engineer, Codeex
**What happened:** Owned all infrastructure-related SOC-2 Type II requirements through a successful audit.
**Why it matters:** compliance, security, cross-team coordination, leading without authority
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Bare-metal Kubernetes and a zero-trust developer platform from zero
**Source:** CV - DevOps Engineer, Goya CJSC
**What happened:** Designed and delivered bare-metal Kubernetes from zero to production, plus an internal developer platform with mTLS, RBAC and network policies.
**Why it matters:** platform engineering, greenfield ownership, security by design (fits the Cybersecurity degree)
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Environment provisioning cut from days to under 30 minutes
**Source:** CV - DevOps Engineer, Goya CJSC
**What happened:** Automated environment provisioning with Ansible playbooks, taking new-environment setup from days to under 30 minutes.
**Why it matters:** automation impact, developer experience, "tell me about a process you improved"
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

### Leading the DevOps team without the title
**Source:** Candidate - Goya CJSC
**What happened:** Led the DevOps team while formally titled DevOps Engineer.
**Why it matters:** leadership, mentoring and team-lead roles, "tell me about a time you led others"
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:

## Common Tough Questions

### "Why did you leave [previous company]?"
> [PREPARE YOUR ANSWER - be honest, forward-looking, no negativity about former employer]

### "You don't have [specific skill/experience]."
> [PREPARE YOUR ANSWER - acknowledge the gap, bridge to adjacent experience, show willingness to learn]

### "Where do you see yourself in 5 years?"
> [PREPARE YOUR ANSWER - show ambition aligned with the role's growth path]

### "What's your biggest weakness?"
> [PREPARE YOUR ANSWER - genuine weakness with concrete mitigation strategy]

### "Why this company specifically?"
> Customize per company. Must reference: specific projects, company values, market position, or team structure. Never give a generic answer.

### Questions specific to this profile
Prepare these before the first interview. Each follows from something a recruiter can see on the CV or on LinkedIn.

- **"You were at Codeex for only 10 months. Why did you leave?"**
  > [PREPARE YOUR ANSWER]
- **"Why are you leaving CodedCloud after just over a year?"**
  > [PREPARE YOUR ANSWER]
- **"Your CV says Senior, but every title is DevOps Engineer."**
  > [PREPARE YOUR ANSWER - e.g. led the Goya DevOps team; ownership of the Codeex SOC-2 audit and DNS platform]
- **"Your AWS and Kubernetes certifications have lapsed."**
  > [PREPARE YOUR ANSWER - renewal plan, or the hands-on work since]
- **"LinkedIn shows Stone Valley LLC overlapping Goya in 2022."**
  > [PREPARE YOUR ANSWER]

## Questions You Should Ask Interviewers

### About the Role
- "What does a typical week look like in this role?"
- "What would success look like in the first 6 months?"
- "What's the biggest challenge the team is facing right now?"

### About the Team
- "How big is the team, and how do you divide work?"
- "What does the development/project lifecycle look like, from idea to production?"
- "How do you onboard new team members?"

### About Tech & Growth
- "What's your current tech stack for [relevant area]?"
- "Is there room to grow into more architectural or strategic decisions?"
- "How does the team stay current with new tools and methods?"

### About Culture (use these to prevent disappointment)
- "How would you describe the team culture?"
- "What does professional development look like here?"
- "Is there flexibility for remote/hybrid work?"
- "What's the balance between development/new projects and maintenance work?"
- "How would you describe the leadership style in this team?"
- "What do people who thrive here have in common?"

## Phone/Video Interview Tips
- Have STAR examples written out (use this file)
- Keep a glass of water nearby
- Smile when speaking (it changes your tone)
- Ask for clarification if a question is vague
- It's OK to take 5 seconds to think before answering
- End with: "Is there anything else you'd like to know about my background?"

## After the Application (Best Practice)

### Follow-Up Etiquette
- **Don't call to "stand out"** or to learn more about the role post-submission - this risks a negative impression
- If the employer specified a timeline, respect it and wait
- If no timeline was given and significant time has passed (2+ weeks), a brief call to ask about status is acceptable
- If you have genuinely new, relevant information to share, a short follow-up is fine

### Thank-You Notes
- When you receive any update (interview invitation, rejection, or status update), send a brief thank-you message
- Express appreciation for their time and the process
- Keep it short (2-3 sentences)

## Roleplay Guidelines
When the user asks for interview practice:
1. Ask which role/company to simulate
2. Start with easy warm-up questions ("Tell me about yourself")
3. Progress to role-specific technical questions
4. Include 1-2 behavioral questions using the competencies from the job posting
5. End with a tough question or curveball
6. After each answer, give brief feedback: what worked, what to sharpen
7. Suggest which STAR example would work best for each question
