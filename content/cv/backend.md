
# Teoh Kai Shun
ks.teoh001@gmail.com · [LinkedIn](https://www.linkedin.com/in/kai-shun-teoh-839860180/) · [GitHub](https://github.com/BeanBois)

ML Engineer at Tencent writing the Go services behind its model-serving platform (tRPC, Protobuf, MySQL, Kubernetes), with side projects in Go, Python, C++, TypeScript and Kotlin: an exchange matching engine, a tamper-evident election ledger, an on-device finance ledger. First-Class CS (KCL), MSc AI & ML (Imperial).

## Experience
**Tencent**, ML Engineer, AI infrastructure · Mar 2026 – present
- Main contributor (about 450 of 550 commits) to a Go/tRPC/Protobuf platform backed by MySQL through which 1,000+ GPUs of model-serving services are deployed and scaled across multiple Kubernetes clusters and business units.
- Made it multi-tenant: every query scoped by business unit with ownership checks, configuration resolved per tenant from a shared base layer.
- Built a time-of-day autoscaling scheduler with conflict-validated schedules, staged scale-up and a database-enforced lock (UNIQUE constraint) against double fires.
- Hardened cross-environment service cloning; replaced N per-service calls with one batch call; made DAO writes transactional; removed hard-coded credentials; led a four-phase refactor of monolith handlers into packages.
- Since Oct 2026, second-in-command on a new gameplay-conversation query service: fixed timezone-wrong DATETIME writes with a tested migration runbook, and LLM worker timeouts.

**9Loop**, Software Engineer Intern · 2024
- Integrated a third-party game API with an automated integration-test suite (coverage 40% → 85%); refactored a Svelte/TypeScript page generator (30% lower render latency).

## Projects
**Wallet**, on-device personal finance (Kotlin Multiplatform + SwiftUI) · 2026 – present
- Parses bank statements on the phone into a local ledger; the balance sheet reconciles by replaying every movement against each closing balance.
- Integer money end to end; build-enforced module boundaries; 600+ unit tests across JVM and iOS.

**myBudiXc**, exchange matching engine (Go) · 2025
- Price-time-priority order book for instant matches plus a deadline-aware batch matcher that pairs unmatched orders to maximise volume; WebSocket market feed.

**polyarb**, Polymarket arbitrage (Python) · 2026
- Depth-aware VWAP bundle costing from the live order book, risk controls for non-atomic multi-leg execution, paper trading by default, SQLite persistence.

**Also**: C++ market-data terminal (Finnhub ticks → TCP socket → Python plotter) · Go terminal budget tracker (Bubble Tea + SQLite) · BlockHub, 1st of 50+ teams at the Polygon × EasyA hackathon

## Education
**Imperial College London**, MSc Computing (AI & ML) · 2024 – 2025
**King's College London**, BSc Computer Science with Intelligent Systems, First Class (77/100) · 2020 – 2023

## Skills
Go, Python, TypeScript, Kotlin, C++, SQL · tRPC, Protobuf, REST, WebSockets · MySQL, PostgreSQL, SQLite · Kubernetes, Docker

## Awards & languages
1st, Polygon × EasyA Hackathon (50+ teams) · Runner-up, HackKing's (BlackRock) · Gold, UKMT Senior Maths
English & Chinese (proficient) · Malay (conversational) · German (basic)
