
# Teoh Kai Shun
ks.teoh001@gmail.com · [LinkedIn](https://www.linkedin.com/in/kai-shun-teoh-839860180/) · [GitHub](https://github.com/BeanBois)

ML Engineer at Tencent and main author of its model-serving platform: deployment, GPU autoscaling and multi-tenancy for 1,000+ GPUs on Kubernetes. Runs his own GPU home lab serving local LLMs over Tailscale. First-Class CS (KCL), MSc AI & ML (Imperial).

## Experience
**Tencent**, ML Engineer, AI infrastructure · Mar 2026 – present
- Main contributor (about 450 of 550 commits) to a Go/tRPC platform through which 1,000+ GPUs of model-serving services are deployed and scaled across multiple Kubernetes clusters and business units.
- Designed and built time-of-day ("tidal") GPU autoscaling from scratch: conflict-validated schedules, a scheduler/executor firing multiple configs per tick, staged two-phase scale-up, a MySQL-enforced lock against concurrent fires, and reconciliation that auto-disables orphaned schedules.
- Built GPU usage history (30-minute snapshots) and fixed the GPU accounting behind resource reports.
- Reliability: request-ID tracing across every RPC, automatic Kubernetes client rebuild on token expiry, namespace guards before deploy, bounded cluster-probe budgets, migration of 29 stuck orphaned records.
- Made the platform multi-tenant, with environment tags bound to the clusters each tenant may deploy into; wrote the bilingual (EN/CN) handover with eleven recorded design decisions.

**9Loop**, Software Engineer Intern · 2024
- Built an automated integration-test suite for a third-party game API (coverage 40% → 85%); refactored a Svelte/TypeScript page generator.

## Projects
**Acute kidney injury predictor**, Imperial · 2024
- Deployed an ML inference service on Kubernetes with Prometheus monitoring, alerting and automated rollback on model degradation; wrote the postmortem for a live failure.

**Ollama home lab** · 2026 – present
- Private GPU inference box (Ollama on Windows + WSL) reachable over a Tailscale mesh; serves qwen3:32b as the default backend for RE-News.

**RE-News**, data pipeline with a switchable model backend · 2026
- Pipeline of per-source encoders into PostgreSQL; each stage's model backend (local Ollama or Claude API) is a config switch.

**Distributed RL training** · 2023
- Spread A3C-style asynchronous training across 3 machines, cutting wall-clock time by about 60%.

## Education
**Imperial College London**, MSc Computing (AI & ML) · 2024 – 2025
**King's College London**, BSc Computer Science with Intelligent Systems, First Class (77/100) · 2020 – 2023

## Skills
Kubernetes, Docker, Prometheus, Linux, Tailscale, Git · Go, Python, SQL (MySQL, PostgreSQL) · tRPC, Protobuf · Studying for CKA

## Awards & languages
1st, Polygon × EasyA Hackathon (50+ teams) · Runner-up, HackKing's (BlackRock) · Gold, UKMT Senior Maths
English & Chinese (proficient) · Malay (conversational) · German (basic)
