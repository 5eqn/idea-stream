# Idea Stream

将海量学术论文封装为可被持续消费的**评分流**（rated paper stream），由 Claude Code / Codex Agent 驱动，从上游（arxiv）无限采集、打分、入库，理论上可穷尽整个上游并持续运行。

## 核心理念

上游有无限的新论文涌现。与其一次性搜索、手动筛选，不如**把论文变成一个流（stream）**——Agent 持续采集、按统一标准打分、写入 SQLite 数据库。下游消费者（研究者、推荐系统、RAG pipeline）按自己的节奏从流中消费，标记已读但不删除。

每条记录包含：
- 论文元信息（id, title, link, date, source）
- **质量评分**（1–10）—— 基于作者声誉和论文实际质量
- **相关性评分**（1–10）—— 基于论文对特定研究主题的相关程度

## 项目结构

```
├── CLAUDE.md              # Agent 指南（主题定义、评分标准、工作流、约定）
├── stream.db              # SQLite 数据库，主存储
├── server.py              # HTTP API 服务，查询流数据
├── state_embodiedai.md    # "embodiedai" 主题的采集进度
├── state_multilayervisual.md  # "multilayervisual" 主题的采集进度
└── README.md
```

## 数据库

`stream.db` 包含三张表：

| 表名 | 用途 |
|------|------|
| `papers` | 论文主表，`(id, topic)` 联合主键，自动去重 |
| `search_state` | 搜索进度追踪，记录每个搜索查询的 cursor 位置 |
| `agent_log` | Agent 操作日志 |

### papers 表核心字段

| 字段 | 说明 |
|------|------|
| `id` | arxiv ID（如 `2604.07993`，不带版本后缀） |
| `topic` | 主题标签（`embodiedai` / `multilayervisual`） |
| `quality_score` | 质量评分 1–10 |
| `relevance_score` | 相关性评分 1–10 |
| `quality_reason` | 质量评分理由 |
| `relevance_reason` | 相关性评分理由 |

## 当前主题

| 主题 | 说明 |
|------|------|
| `embodiedai` | 具身智能：服务于 Unitree G1 29DOF 人形机器人（无灵巧手）的 locomotion 与操作研究 |
| `multilayervisual` | 多层视觉压缩：将原始大视觉输入压缩至极低比特率的有用视觉流，服务于视频理解 / VLA / World Model |

## 评分标准

每个主题有两维评分（均 1–10 分），评分标准详见 `CLAUDE.md` 的 Rating Standard 章节：

- **Quality**：从 10（里程碑级）到 1（垃圾/离题），综合考虑作者声誉、实验完备性、写作质量
- **Relevance**：从 10（精准命中）到 1（无关），基于论文对主题的实际匹配程度

## API

`server.py` 提供 HTTP API：

```bash
python server.py
# 默认监听 0.0.0.0:8080
```

| 端点 | 说明 |
|------|------|
| `GET /api/papers?topic=&min_quality=&min_relevance=&limit=&offset=` | 分页查询论文流 |
| `GET /api/stats` | 数据库统计信息 |
| `GET /api/topics` | 列出所有主题 |

查询示例：

```bash
# 获取 embodiedai 主题下质量 ≥7、相关性 ≥8 的最新 20 篇论文
curl "http://localhost:8080/api/papers?topic=embodiedai&min_quality=7&min_relevance=8&limit=20"
```

## 使用方法

### 启动采集 Agent

使用 Claude Code 的 `/loop` 命令让 Agent 持续运行：

```bash
# 进入项目目录
cd /path/to/idea-stream

# 启动 Claude Code
claude

# 或使用 /loop 定时触发（每 10 分钟执行一轮）
/loop 10m Complete all tasks in CLAUDE.md for the "embodiedai" topic
```

Agent 会自动：
1. 读取对应主题的 `state_*.md` 了解当前进度
2. 从 arxiv recent listing 页面发现新论文
3. 读取摘要、按标准打分
4. 写入 `stream.db`（`INSERT OR IGNORE` 自动去重）
5. 更新状态文件，下一轮 Agent 接续工作

要同时收集多个主题，你需要启动多个 Agent。

### 消费流数据

研究者或下游系统通过 API 消费论文流：

```python
import requests

# 按阈值拉取高质量高相关论文
resp = requests.get("http://localhost:8080/api/papers", params={
    "topic": "embodiedai",
    "min_quality": 7,
    "min_relevance": 8,
    "limit": 50
})
papers = resp.json()
```

## 工作流约定

- **每个 Agent 专注一个主题**，不要跨主题切换
- 在主题的 `state_*.md` 中声明占用（Active agents），完成后移除
- 每批处理 10–20 篇
- 从最新论文向旧论文推进
- 主要来源：arxiv listing 页面（`/list/cs.CV/recent`, `/list/cs.RO/recent`）
- 间隔至少 20 分钟以避免触发限流
- 不要使用 sub-agent（`Do not invoke subagents`）

## 质量-数量平衡

系统服务于顶级学术研究团队。下游消费者按自己的节奏消费流数据，如果采集太慢，他们会抱怨流干了；如果评分太随意，他们会抱怨质量下降。Agent 需要在速度和质量之间保持平衡——这是 CLAUDE.md 中评分标准的粒度（1–10 分带详细准则）存在的理由。

如果你需要调整偏好（偏质量还是偏数量），在 `CLAUDE.md` 的 Notes 区域留下记录，后续 Agent 会遵循。
