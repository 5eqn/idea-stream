## Topic register

- "embodiedai": Advances in embodied intelligence that are helpful to Unitree G1 29DOF humanoid robot without dexterous hand. A research targeting Unitree G1 specifically would satisfy this. A research doing cross-embodiment humanoid-robot foundation model would satisfy this. A research focusing on locomotion and dexterous hand manipulation would satisfy this, because even if it features dexterous hand, the locomotion and arm-moving part is helpful to robot without dexterous hand. A research for robotic arm would not satisfy this. A research for pure VLM without embodiment would not satisfy this.
- "multilayervisual": Advances in visual processing in the direction that: an intelligent visual agent should eventually be able to utilize raw, large visual input, and compresses multi-layered such information all the way down to around 10 bits per second, yet useful, visual data stream, that aids with video  understanding and VLA / World Model and such, ultimately helping the humanity build visual AGI. Judge yourself if an article aligns with requested direction.

## Source register

- "arxiv": Paper from arxiv (id = arxiv paper id, without version suffix e.g. use 2604.07993 not 2604.07993v1)

## Rating standard

### Quality (1-10): How good is this work, considering author reputation and paper quality?

| Score | Label | Criteria |
|-------|-------|----------|
| 10 | Landmark | Seminal work from top-tier group (e.g., Google DeepMind, OpenAI, top academic labs) that defines or redefines a subfield. Exceptional experimental validation, clarity, and significance. Will be widely cited for years. |
| 9 | Outstanding | From renowned authors/groups with strong track record. Novel contribution with thorough experiments on real systems. Publishable at top venues (CoRL, ICRA, RSS, NeurIPS, CVPR) as best-paper candidate. |
| 8 | Excellent | High-quality work from recognized group or strong independent contribution. Solid methodology, meaningful baselines, convincing results. Clearly above-average for the venue. |
| 7 | Strong | Competent work with clear contribution. Reasonable experiments, acceptable writing quality. Meets the bar for good venues but not exceptional. Most good workshop/venue papers land here. |
| 6 | Good | Decent contribution with some limitations. May have incomplete experiments, minor methodological weaknesses, or less-known authors. Still adds value to the field. |
| 5 | Adequate | Publishable but unremarkable. Incremental extension of existing work with limited novelty. Experiments are present but not comprehensive. |
| 4 | Below average | Noticeable gaps: weak baselines, small-scale validation, poor writing, or unclear motivation. Would likely be rejected at solid venues. |
| 3 | Weak | Significant issues: unsupported claims, missing comparisons, toy-only experiments, or poorly executed idea. |
| 2 | Poor | Fundamentally flawed methodology, nonsensical claims, or near-plagiarism of existing work without acknowledgment. |
| 1 | Reject | Spam, completely off-topic, gibberish, or retracted. Not worth reading. |

### Relevance (1-10): How well does this paper align with the topic register?

| Score | Label | Criteria |
|-------|-------|----------|
| 10 | Perfect bullseye | Directly solves a core problem for the exact target (e.g., whole-body control for Unitree G1 humanoid, or a visual compression architecture explicitly designed for embodied agent perception streams). |
| 9 | Highly relevant | Addresses the exact topic with a slight broadening (e.g., cross-embodiment humanoid foundation model including G1-class robots, or multi-layer visual token compression for VLA/world models). |
| 8 | Very relevant | Core method transfers directly (e.g., locomotion policy for bipedal humanoid, or visual encoder benchmarking showing compression-utility tradeoff for embodied tasks). |
| 7 | Relevant | Meaningful overlap but needs adaptation (e.g., dexterous manipulation including locomotion, or video understanding architectures applicable to embodied perception). |
| 6 | Somewhat relevant | Tangentially useful (e.g., sim-to-real for legged robots, or efficient attention mechanisms for visual transformers that could apply to embodied perception). |
| 5 | Moderately related | Same broad area but different focus (e.g., quadruped locomotion, or general image compression without embodied-agency motivation). |
| 4 | Loosely related | Shares techniques but different domain (e.g., robotic arm-only manipulation, or pure VLM without embodiment linkage). |
| 3 | Weakly related | Peripheral (e.g., RL for games, or image classification benchmarks). |
| 2 | Barely related | Same high-level field but no practical connection (e.g., NLP, or audio processing). |
| 1 | Unrelated | No connection to either topic register entry. |


## Task

- [x] Reify rating standard for quality & relevance for each score point
- [ ] Add rows in stream.db infinitely with non-duplicative items, each row with topic, source, date, id (non duplicative), link, quality (X out of 10) + short reason (based on whether this work is from renouned authors and the actual quality of this work), relevance (X out of 10) + short reason (based on the topic register), date. This work will be done by multiple agents sequentially or in parallel, so keep suitable state documentations to make this system theoretically possible to run forever steadily (without searching over the same thing again and again) and exhaust the whole upstream source and rate every single item in it.

## Notes

- Think of you're providing a service to top academic research group. They will drain stream.db based on their cadence (not actually removing items from db, but marking them internally as read, simulating a stream). There will be a quality-quantity balance, if you choose quality, they may complain that you're giving new rows too slow; if you choose quantity, they may complain the degrade of quality. So try to think for their needs, if you get steered by user preference, keep suitable documentations for preference fulfilling so other agents would know.
- Do not invoke subagents.

## Stream Ingestion State (General)
This section tracks general progress and conventions for arxiv paper ingestion across agents.

### How to use state files
- Each agent reads the relevant state file for their assigned topic before starting work to know what's already been covered.
- After completing a batch, update the relevant per-topic state file with the new cursor position.
- The `search_state` table in `stream.db` is the authoritative source of truth; state files provide human-readable context.

### State File Structure
- **General state**: Defined in this CLAUDE.md (conventions, API notes, known issues, cross-topic rules).
- **Per-topic state**: Each topic has a dedicated `state_<topic>.md` file that tracks:
  - Search queries used (with pagination status)
  - Total papers processed
  - Date range covered
  - Last processed paper date
  - Active agents working on the topic

### Agent Rules
- **Single topic focus**: Each agent should work on **one topic only** at a time. Do not switch between topics during a work session unless explicitly instructed.
- Claim a topic by adding your agent ID to the "Active agents" section of the topic's state file before starting work.
- Remove your agent ID from the "Active agents" section when you finish your batch.

### Conventions
- **Agent ID**: Use a unique identifier (e.g., `agent-YYYYMMDD-HHMMSS`) when inserting papers and logging.
- **Batch size**: Aim for 10-20 papers per batch to balance speed and quality.
- **Dedup**: The database enforces `(id, topic)` uniqueness. If a paper is relevant to both topics, insert it twice with different topics and potentially different relevance scores.
- **Rating rigor**: Follow the rating standard in CLAUDE.md strictly. Read the paper abstract (at minimum) before rating.
- **Date order**: Process newest papers first, working backwards in time.
- **Search strategy**: Use the arxiv API (`http://export.arxiv.org/api/query`) with `start` and `max_results` parameters to paginate through results. Track the `last_start` value in `search_state` table.

### Arxiv API notes
- Base URL: `http://export.arxiv.org/api/query`
- Parameters: `search_query`, `start`, `max_results`, `sortBy` (relevance/submittedDate), `sortOrder` (descending)
- Rate limit: Be respectful — no more than 1 request per 3 seconds.
- Each query returns up to 2000 results max. Use pagination with `start` offset.
- Paper ID format: e.g., `2505.12345` or `cs/0701001`

### Known issues
- Arxiv API consistently times out. Use WebSearch + webReader as fallback for fetching paper abstracts.
- WebSearch rate limits (429 errors) — space requests to avoid hitting limits.