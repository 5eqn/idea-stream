# Stream Ingestion State

This file tracks the progress of arxiv paper ingestion across agents.

## How to use this file

- Each agent reads this file before starting work to know what's already been covered.
- After completing a batch, update the relevant section with the new cursor position.
- The `search_state` table in `stream.db` is the authoritative source of truth; this file provides human-readable context.

## Topic cursors

### embodiedai

- **Search queries used**: `humanoid robot whole body control` (paginated to start=20), `humanoid robot locomotion reinforcement learning` (paginated to start=20), `humanoid robot perceptive locomotion depth terrain`, `embodied AI humanoid foundation model`, `bipedal robot policy learning`, `cross-embodiment humanoid robot policy learning manipulation foundation model`, `humanoid robot scaling laws locomotion embodiment generalization`, `humanoid robot contact-rich manipulation whole body`, `WholebodyVLA ICLR 2026 OpenDriveLab`, `humanoid robot whole body loco-manipulation policy learning foundation model`, `humanoid robot whole body control reinforcement learning policy`, `HoloMotion humanoid whole body control foundation model`, `humanoid robot sim-to-real transfer whole body policy deployment`, `Efficient Learning Unified Policy Whole-body Manipulation quadruped`, `Unitree G1 humanoid robot control locomotion manipulation policy`, `humanoid robot fall recovery get up robust locomotion`, `bipedal robot walking locomotion robust terrain adaptation depth perception`, `humanoid robot learning from human video demonstration imitation whole body`, `humanoid robot impedance control whole body interaction force`, `humanoid robot parkour agile locomotion reinforcement learning` (batch 088), `humanoid robot arm swinging locomotion momentum whole body coordination` (batch 089), `humanoid robot pushing heavy object whole body manipulation force control` (batch 089), `humanoid robot door opening manipulation whole body force` (batch 120), `humanoid robot bimanual manipulation dual arm coordination` (batch 122), `humanoid robot carrying heavy object whole body locomotion load` (batch 121), `3D scene representation survey embodied AI` (batch 123), `humanoid robot terrain estimation depth perception adaptive locomotion` (batch 123, rate-limited), `humanoid robot running sprinting agile locomotion policy reinforcement learning` (batch 136), `humanoid robot get up recovery fall prone supine policy learning` (batch 136), `humanoid robot object pushing heavy manipulation whole body force compliance policy` (batch 136), `humanoid robot kicking soccer ball whole body dynamic balance policy` (batch 137), `humanoid robot jumping leaping explosive motion whole body control policy` (batch 138), `humanoid robot impedance stiffness joint control whole body interaction` (batch 139), `humanoid robot visual navigation obstacle avoidance depth perception loco-manipulation` (batch 139), `humanoid robot visual SLAM mapping localization whole body navigation` (batch 141), `humanoid robot turning pivoting agile motion policy reinforcement learning` (batch 141, all dupes), `humanoid robot grasping lifting manipulation without dexterous hand whole body` (batch 142), `humanoid robot whole body teleoperation imitation learning policy transfer` (batch 143, all dupes), `Unitree G1 humanoid robot control locomotion manipulation` (batch 143, all dupes), `humanoid robot multi-contact locomotion climbing stairs steep terrain policy` (batch 144, most dupes),
`humanoid robot expressive gesture motion generation` (batch 148),
`humanoid robot screwdriver tool use manipulation policy` (batch 149),
`humanoid robot safety collision avoidance whole body control policy learning` (batch 150),
`humanoid robot brachiation swinging arm locomotion agile movement` (batch 151)
- **Papers processed**: 351
- **Date range covered**: 2024-04-08 to 2026-05-18
- **Last processed paper date**: 2026-05-18
- **Active agents**: agent-20260518-151

### multilayervisual

- **Search queries used**: `visual token compression VLA` (start=0, 50 seen), `world model visual latent representation robotics` (start=0, 50 seen), `efficient visual processing embodied AI token pruning` (start=0, 50 seen), `VLA vision-language-action token compression pruning` (start=20, 20 seen), `visual token compression efficient vision transformer`, `visual token compression multimodal LLM efficient inference pruning`, `VisPruner ICCV 2025 VLM token pruning`, `STEP-Nav AAAI 2025 spatial temporal token pruning`, `Balanced Token Pruning NeurIPS 2025 VLM`, `visual token pruning efficient vision transformer embodied AI`, `visual token reduction efficient vision language model embodied robot`, `TopV compatible token pruning CVPR 2025`, `SparseVLM visual token sparsification ICML 2025`, `visual representation learning robotics world model latent space compression`, `visual token compression video understanding efficient inference streaming`, `visual token pruning efficient video understanding embodied AI robot` (batch 087), `visual representation compression world model latent space robotics` (batch 089), `information bottleneck visual compression VLA embodied agent` (batch 120), `foveated rendering robot perception visual compression efficient` (batch 121), `visual scene graph compression efficient representation robot perception` (batch 123), `efficient visual encoder architecture lightweight embodied agent robot perception` (batch 141), `adaptive visual resolution attention embodied robot real-time perception efficient` (batch 142), `visual representation learning world model robotics compression survey` (batch 143), `latent visual token quantization discrete bottleneck robot policy` (batch 144),
`visual token merging redundancy reduction VLA efficient inference` (batch 148),
`action-aware dynamic pruning VLA token efficient inference` (batch 149),
`visual state space model S6 efficient vision transformer embodied agent robot` (batch 150),
`visual token distillation knowledge transfer efficient student teacher VLA embodied` (batch 151)
- **Papers processed**: 267
- **Date range covered**: 2024-03-11 to 2026-05-18
- **Last processed paper date**: 2026-05-18
- **Active agents**: agent-20260518-151

## Conventions

- **Agent ID**: Use a unique identifier (e.g., `agent-YYYYMMDD-HHMMSS`) when inserting papers and logging.
- **Batch size**: Aim for 10-20 papers per batch to balance speed and quality.
- **Dedup**: The database enforces `(id, topic)` uniqueness. If a paper is relevant to both topics, insert it twice with different topics and potentially different relevance scores.
- **Rating rigor**: Follow the rating standard in CLAUDE.md strictly. Read the paper abstract (at minimum) before rating.
- **Date order**: Process newest papers first, working backwards in time.
- **Search strategy**: Use the arxiv API (`http://export.arxiv.org/api/query`) with `start` and `max_results` parameters to paginate through results. Track the `last_start` value in `search_state` table.

## Arxiv API notes

- Base URL: `http://export.arxiv.org/api/query`
- Parameters: `search_query`, `start`, `max_results`, `sortBy` (relevance/submittedDate), `sortOrder` (descending)
- Rate limit: Be respectful — no more than 1 request per 3 seconds.
- Each query returns up to 2000 results max. Use pagination with `start` offset.
- Paper ID format: e.g., `2505.12345` or `cs/0701001`

## Known issues

- Arxiv API consistently times out. Use WebSearch + webReader as fallback for fetching paper abstracts.
- WebSearch rate limits (429 errors) — space requests to avoid hitting limits.
