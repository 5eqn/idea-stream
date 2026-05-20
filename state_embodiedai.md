# Embodied AI Topic State
This file tracks the progress of arxiv paper ingestion for the "embodiedai" topic.

## Topic cursors: embodiedai
- **Search queries used**: `humanoid robot whole body control` (paginated to start=20), `humanoid robot locomotion reinforcement learning` (paginated to start=20), `humanoid robot perceptive locomotion depth terrain`, `embodied AI humanoid foundation model`, `bipedal robot policy learning`, `cross-embodiment humanoid robot policy learning manipulation foundation model`, `humanoid robot scaling laws locomotion embodiment generalization`, `humanoid robot contact-rich manipulation whole body`, `WholebodyVLA ICLR 2026 OpenDriveLab`, `humanoid robot whole body loco-manipulation policy learning foundation model`, `humanoid robot whole body control reinforcement learning policy`, `HoloMotion humanoid whole body control foundation model`, `humanoid robot sim-to-real transfer whole body policy deployment`, `Efficient Learning Unified Policy Whole-body Manipulation quadruped`, `Unitree G1 humanoid robot control locomotion manipulation policy`, `humanoid robot fall recovery get up robust locomotion`, `bipedal robot walking locomotion robust terrain adaptation depth perception`, `humanoid robot learning from human video demonstration imitation whole body`, `humanoid robot impedance control whole body interaction force`, `humanoid robot parkour agile locomotion reinforcement learning` (batch 088), `humanoid robot arm swinging locomotion momentum whole body coordination` (batch 089), `humanoid robot pushing heavy object whole body manipulation force control` (batch 089), `humanoid robot door opening manipulation whole body force` (batch 120), `humanoid robot bimanual manipulation dual arm coordination` (batch 122), `humanoid robot carrying heavy object whole body locomotion load` (batch 121), `3D scene representation survey embodied AI` (batch 123), `humanoid robot terrain estimation depth perception adaptive locomotion` (batch 123, rate-limited), `humanoid robot running sprinting agile locomotion policy reinforcement learning` (batch 136), `humanoid robot get up recovery fall prone supine policy learning` (batch 136), `humanoid robot object pushing heavy manipulation whole body force compliance policy` (batch 136), `humanoid robot kicking soccer ball whole body dynamic balance policy` (batch 137), `humanoid robot jumping leaping explosive motion whole body control policy` (batch 138), `humanoid robot impedance stiffness joint control whole body interaction` (batch 139), `humanoid robot visual navigation obstacle avoidance depth perception loco-manipulation` (batch 139), `humanoid robot visual SLAM mapping localization whole body navigation` (batch 141), `humanoid robot turning pivoting agile motion policy reinforcement learning` (batch 141, all dupes), `humanoid robot grasping lifting manipulation without dexterous hand whole body` (batch 142), `humanoid robot whole body teleoperation imitation learning policy transfer` (batch 143, all dupes), `Unitree G1 humanoid robot control locomotion manipulation` (batch 143, all dupes), `humanoid robot multi-contact locomotion climbing stairs steep terrain policy` (batch 144, most dupes),
`humanoid robot expressive gesture motion generation` (batch 148),
`humanoid robot screwdriver tool use manipulation policy` (batch 149),
`humanoid robot safety collision avoidance whole body control policy learning` (batch 150),
`humanoid robot brachiation swinging arm locomotion agile movement` (batch 151),
`humanoid robot locomotion unified walking running recovery whole body state estimation` (batch 152),
`ti:humanoid broad title search` (batches 153-175)
- **Papers processed**: 2291
- **Date range covered**: 2007-08-06 to 2011-12-09
- **Last processed paper date**: 2011-12-09 (cat:cs.RO AND all:humanoid ANDNOT ti:humanoid final batch, start=950, EXHAUSTED 961/961)
- **Active agents**: agent-20260519-loop2m
- ti:humanoid broad title search EXHAUSTED — reached API pagination limit both descending and ascending, ~845 of 885 results covered
`ti:"bipedal walking"` (batches 158-162, EXHAUSTED 49/49), `ti:"bipedal robot"` (batches 163-174, EXHAUSTED 90/90)
`ti:"whole body control"` (batch 175, resumed, 84 total, 20/84 processed — HIGH overlap with ti:humanoid confirmed: 10/10 dupes at start=10)
`all:"centroidal dynamics" AND all:legged` (batch 176, EXHAUSTED 14/14)
`all:"hybrid zero dynamics" AND all:walking` (batch 177-179, EXHAUSTED 29/29)
`all:"capture point" AND all:walking` (batch 180, EXHAUSTED 8/8)
`all:"ZMP" AND all:bipedal` (batch 181, EXHAUSTED 7/7)
`cat:cs.RO AND all:bipedal ANDNOT ti:bipedal ANDNOT ti:humanoid ANDNOT ti:quadruped` (batches 182-210, EXHAUSTED 245/245)
`cat:cs.RO AND all:humanoid ANDNOT ti:humanoid` (batches 211-229, EXHAUSTED 961/961, ~70% new yield, added 349 papers)
- **Active agents**: agent-20260519-loop2m
