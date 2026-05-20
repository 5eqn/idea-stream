# BFMenance Topic State
This file tracks the progress of arxiv paper ingestion for the "bfmenhance" topic.

## Topic cursors: bfmenhance
- **Search queries used**: `cs.RO recent listing skip=0,50,100,150,200,250,300` (batches 001-006, EXHAUSTED at skip=250+), `cs.LG recent listing skip=0` (batch 001), `cs.CV recent listing skip=0,50` (batches 002, 004, no robot hits), `cs.AI recent listing skip=0` (batch 003, no hits), `ti:"data augmentation" AND (robot OR policy OR humanoid)` (batch 004), `ti:"domain adaptation" AND robot AND policy` (batch 004), `ti:"information bottleneck" AND (robot OR policy OR RL)` (batch 004), `ti:"unsupervised" AND (robot OR humanoid) AND (policy OR RL)` (batch 005, mostly non-robot), `ti:"co-training" AND (robot OR policy OR humanoid)` (batch 005), `ti:"system identification" AND (sim-to-real OR sim2real OR robot policy)` (batch 004), `ti:"self-supervised" AND (humanoid OR robot policy OR locomotion)` (batch 006, no robot hits), `ti:"meta reinforcement learning" AND (sim-to-real OR robot policy OR humanoid)` (batch 006, no direct robot hits), cross-topic reuse from embodiedai stream.db (ongoing, high-quality papers from Q8+ queue)
- **Papers processed**: 245
- **Date range covered**: 2019-06-10 to 2026-05-20
- **Last processed paper date**: 2026-05-19
- **Active agents**: agent-20260520-loop5m
- **Status note 2026-05-20 batch 25**: +47 papers (198→245). Cross-topic mining from embodiedai DB through Jan 2026 back to Aug 2025. Highlights: Architecture Is All You Need (2510.14947, AMBER Lab, R10 — timescale separation beats scaling model size), TrajBooster (2509.11839, R10 — cross-embodiment EE trajectory bridge, 10min G1 teleop), RuN (2509.20696, R10 — residual policy on pre-trained motion prior), Traversing Narrow Paths (2508.20661, R10 — lightweight learned modifier on physics template), HDMI (2509.16757, Guanya Shi/Deva Ramanan, R9 — human video → G1 whole-body interaction), MimicDroid (2509.09769, Yuke Zhu, R9 — ICL from human play videos), AMS (2511.17373, R9 — heterogeneous data + adaptive sampling on G1), E-SDS (2511.16446, R9 — VLM automated reward design on G1). 245 papers (130 Q8+, 180 R8+, 109 both). Pipeline has reached Aug 2025 in cross-topic mining.

## Topic Definition
Enhancing performance of behaviour foundation model for humanoid robot (Unitree G1 29DOF) in Sim2Real, making it 10x more compute-effective than scaling training data alone. Baseline: HoloMotion & GEAR-SONIC with domain randomization.

Relevant areas covered:
- [x] Sim-to-real transfer techniques (DR, system identification, privileged distillation)
- [x] Feature engineering for robot policy learning
- [x] Co-training / multi-task / auxiliary task training
- [x] Data augmentation for robot learning
- [x] Sample-efficient and compute-efficient RL for humanoids
- [x] Teacher-student / privileged information distillation
- [x] Curriculum learning for humanoid locomotion/manipulation
- [x] Representation learning for sim-to-real policy transfer
- [x] World models for humanoid robot policy learning
- [x] Creative training paradigms beyond scaling data

## Exhausted Searches
- cs.RO recent listing: traversed skip=0 through skip=300 (pages 0-13), yield dropped to ~6 cross-listed entries at skip=250+
- cs.AI recent listing: skip=0 checked, no humanoid/robot training hits
- cs.CV recent listing: skip=0,50 checked, no humanoid/robot training policy hits
- ti:self-supervised + (humanoid OR robot policy OR locomotion): mostly non-robot perception papers
- ti:meta reinforcement learning + (sim-to-real OR robot policy OR humanoid): no direct robot policy hits
