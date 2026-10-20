
# Teoh Kai Shun
ks.teoh001@gmail.com · [LinkedIn](https://www.linkedin.com/in/kai-shun-teoh-839860180/) · [GitHub](https://github.com/BeanBois)

ML Engineer at Tencent, building the platform that deploys and scales 1,000+ GPUs of model serving. First-Class CS (King's College London) and MSc Computing (AI & ML) from Imperial College London. Research in imitation learning and hyperbolic graph networks; builds models from the paper up (Transformer, SRGAN, AlphaZero-style chess) and takes them to production on Kubernetes.

## Experience
**Tencent**, ML Engineer, AI infrastructure · Mar 2026 – present
- Main contributor (about 450 of 550 commits) to a Go/tRPC platform through which 1,000+ GPUs of model-serving services are deployed and scaled across multiple Kubernetes clusters and business units.
- Designed and built time-of-day GPU autoscaling from scratch: conflict-validated schedules, a multi-config scheduler/executor, staged two-phase scale-up and a database-enforced lock against concurrent fires.
- Made the platform multi-tenant (per-tenant query scoping and layered config); added request-ID tracing, GPU usage history and self-healing cluster clients.
- Since Oct 2026, second-in-command on a new query service for gameplay-session conversation data (Go, MySQL, LLM workers).

**9Loop**, Software Engineer Intern · 2024
- Refactored a Svelte/TypeScript page generator (30% lower render latency); built an integration-test suite for a game API (coverage 40% → 85%).

## Research
**In-context imitation learning with non-Euclidean methods**, Imperial MSc project · 2024 – 2025
- Designed a dual-channel architecture embedding actions and observations separately for few-shot imitation learning.
- Developed a Hyperbolic Graph Attention Network (Poincaré ball) and a Product Manifold Attention module combining Euclidean and hyperbolic channels.
- Used Sarkar's construction for training-free hyperbolic embeddings; benchmarked against Instant Policy (the baseline scored higher; the work showed the approach is feasible).

**Acute kidney injury predictor**, Imperial · 2024
- Gradient-boosted classifier on NHS creatinine data (87% AUC), deployed on Kubernetes with Prometheus monitoring and automated rollback; wrote the live-failure postmortem.

**Neuromorphic computing**, independent study, Imperial · 2024 · winner-take-all spiking network in Lava (Loihi 2) for face-mask classification.

## Projects
**TradingJoe**, multi-strategy portfolio system · 2026
- Black-Litterman, Fama-French and momentum strategies with GNN and LLM view generators, walk-forward backtests and Moomoo paper trading.
- Red-teamed my own results with five review agents (leakage, ML, LLM, finance, execution), found no out-of-sample edge, and published a retraction.

**RE-News**, cited issue ranking for Malaysia · 2026
- Per-source encoders compress news, economic and opinion data into one citable signal schema; an LLM fuses only signals, so every claim resolves to evidence. Runs on a local qwen3:32b by default.

**From scratch**: SRGAN (4×, 29.3 dB PSNR / 0.82 SSIM on DIV2K) · AlphaZero-style chess (MCTS, parallel GPU self-play) · the original Transformer · licence-plate OCR (YOLOv8 + CNN, 94% char accuracy) · A3C-style FPS agent across 3 machines (~60% faster training)

## Education
**Imperial College London**, MSc Computing (AI & ML) · 2024 – 2025
**King's College London**, BSc Computer Science with Intelligent Systems, First Class (77/100) · 2020 – 2023

## Skills
Python, PyTorch, Go, C++, SQL · computer vision, geometric deep learning, RL, LLM systems (RAG, grounding, local serving) · Kubernetes, Docker, Prometheus

## Awards & languages
1st, Polygon × EasyA Hackathon (50+ teams) · Runner-up, HackKing's (BlackRock) · Gold, UKMT Senior Maths
English & Chinese (proficient) · Malay (conversational) · German (basic)
