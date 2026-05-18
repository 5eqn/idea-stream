#!/usr/bin/env python3
"""Self-contained HTTP server for stream.db paper browser."""

import sqlite3
import json
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "stream.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_papers(topic=None):
    db = get_db()
    if topic and topic != "all":
        rows = db.execute(
            "SELECT * FROM papers WHERE topic = ? ORDER BY paper_date DESC", (topic,)
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM papers ORDER BY paper_date DESC").fetchall()
    db.close()
    papers = []
    for r in rows:
        papers.append({
            "id": r["id"],
            "topic": r["topic"],
            "source": r["source"],
            "paper_date": r["paper_date"],
            "link": r["link"],
            "title": r["title"],
            "quality_score": r["quality_score"],
            "quality_reason": r["quality_reason"],
            "relevance_score": r["relevance_score"],
            "relevance_reason": r["relevance_reason"],
            "date_added": r["date_added"],
        })
    return papers


def get_topics():
    db = get_db()
    rows = db.execute(
        "SELECT topic, COUNT(*) as cnt FROM papers GROUP BY topic ORDER BY cnt DESC"
    ).fetchall()
    db.close()
    return [{"topic": r["topic"], "count": r["cnt"]} for r in rows]


# --- Sorting algorithms ---

def sort_quality(papers):
    return sorted(papers, key=lambda p: (-p["quality_score"], -p["relevance_score"], p["paper_date"]))


def sort_relevance(papers):
    return sorted(papers, key=lambda p: (-p["relevance_score"], -p["quality_score"], p["paper_date"]))


def sort_date(papers):
    return sorted(papers, key=lambda p: (p["paper_date"], -p["relevance_score"], -p["quality_score"]), reverse=True)


def _days_ago(date_str):
    """Approximate days since paper_date from a fixed 'now' of 2026-05-18."""
    y, m, d = date_str.split("-")
    # simple ordinal approximation
    paper_ord = int(y) * 400 + int(m) * 31 + int(d)
    now_ord = 2026 * 400 + 5 * 31 + 18
    return max(now_ord - paper_ord, 0)


def sort_must_read(papers):
    """Must-Read Score: sqrt(quality * relevance) with a recency boost.
    Formula: must_read = sqrt(Q * R) * (1 + 0.4 * exp(-days/120))
    - Geometric mean ensures both dimensions matter; a (10,1) paper scores ~1.58, (7,7) scores 7.
    - Recency boost fades with 120-day half-life so timeless gems still surface.
    """
    def score(p):
        q, r = p["quality_score"], p["relevance_score"]
        geo = math.sqrt(q * r)
        recency = 1.0 + 0.4 * math.exp(-_days_ago(p["paper_date"]) / 120.0)
        return geo * recency
    return sorted(papers, key=score, reverse=True)


def sort_discovery(papers):
    """Discovery Rank: surfaces relevant recent papers even if quality is moderate.
    Formula: discovery = R^1.3 * (1 + 0.8 * exp(-days/60)) * (1 + 0.15 * Q)
    - Relevance is raised to 1.3 power to strongly prefer on-target papers.
    - Recency decay is faster (60 days) to highlight fresh findings.
    - Quality enters as a mild multiplier so a (5,9) recent paper beats a (9,6) old one.
    """
    def score(p):
        q, r = p["quality_score"], p["relevance_score"]
        rel = r ** 1.3
        recency = 1.0 + 0.8 * math.exp(-_days_ago(p["paper_date"]) / 60.0)
        qual = 1.0 + 0.15 * q
        return rel * recency * qual
    return sorted(papers, key=score, reverse=True)


SORT_FNS = {
    "quality": sort_quality,
    "relevance": sort_relevance,
    "date": sort_date,
    "must_read": sort_must_read,
    "discovery": sort_discovery,
}


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Idea Stream</title>
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #252535;
    --text: #e8e8f0;
    --text2: #9898b0;
    --accent: #6c5ce7;
    --accent2: #a29bfe;
    --green: #00b894;
    --amber: #fdcb6e;
    --red: #ff6b6b;
    --blue: #74b9ff;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }

  /* --- Header --- */
  .header {
    padding: 28px 32px 20px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(108,92,231,0.06) 0%, transparent 100%);
  }
  .header h1 {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--text);
  }
  .header h1 span { color: var(--accent2); }
  .header .sub {
    font-size: 13px;
    color: var(--text2);
    margin-top: 4px;
  }

  /* --- Toolbar --- */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 32px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    background: var(--surface);
  }

  .toolbar label {
    font-size: 12px;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
  }

  .sort-group, .filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .pill-btn {
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text2);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }
  .pill-btn:hover {
    border-color: var(--accent);
    color: var(--text);
  }
  .pill-btn.active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }
  .pill-btn .algo-tag {
    display: inline-block;
    font-size: 9px;
    background: rgba(255,255,255,0.15);
    padding: 1px 5px;
    border-radius: 3px;
    margin-left: 4px;
    vertical-align: middle;
    letter-spacing: 0.3px;
  }

  .spacer { flex: 1; }

  .stat {
    font-size: 12px;
    color: var(--text2);
  }
  .stat b { color: var(--accent2); }

  /* --- Table --- */
  .table-wrap {
    padding: 0 32px 40px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
  }

  thead th {
    text-align: left;
    padding: 12px 10px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text2);
    font-weight: 600;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 1;
  }
  thead th.center { text-align: center; }

  tbody tr {
    border-bottom: 1px solid rgba(37,37,53,0.5);
    transition: background 0.12s;
  }
  tbody tr:hover {
    background: rgba(108,92,231,0.05);
  }

  tbody td {
    padding: 14px 10px;
    vertical-align: top;
    font-size: 14px;
  }
  tbody td.center {
    text-align: center;
    vertical-align: middle;
  }

  /* Rank number */
  .rank {
    font-size: 12px;
    color: var(--text2);
    font-variant-numeric: tabular-nums;
    min-width: 28px;
    display: inline-block;
  }

  /* Title */
  .title-cell a {
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
    line-height: 1.45;
    transition: color 0.15s;
  }
  .title-cell a:hover {
    color: var(--accent2);
  }
  .title-meta {
    display: flex;
    gap: 8px;
    margin-top: 5px;
    align-items: center;
  }
  .title-meta .tag {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
  }
  .tag-embodiedai {
    background: rgba(0,184,148,0.12);
    color: var(--green);
  }
  .tag-multilayervisual {
    background: rgba(116,185,255,0.12);
    color: var(--blue);
  }
  .title-meta .date {
    font-size: 11px;
    color: var(--text2);
    font-variant-numeric: tabular-nums;
  }

  /* Score badges */
  .score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 34px;
    height: 28px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
  .score-badge.q-high  { background: rgba(0,184,148,0.14); color: var(--green); }
  .score-badge.q-mid   { background: rgba(253,203,110,0.14); color: var(--amber); }
  .score-badge.q-low   { background: rgba(255,107,107,0.1); color: var(--red); }
  .score-badge.r-high  { background: rgba(108,92,231,0.14); color: var(--accent2); }
  .score-badge.r-mid   { background: rgba(253,203,110,0.14); color: var(--amber); }
  .score-badge.r-low   { background: rgba(255,107,107,0.1); color: var(--red); }

  /* Reason tooltip */
  .reason-wrap {
    position: relative;
    cursor: default;
  }
  .reason-wrap .reason-tip {
    display: none;
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    line-height: 1.5;
    color: var(--text);
    width: 260px;
    z-index: 10;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    font-weight: 400;
    text-align: left;
  }
  .reason-wrap:hover .reason-tip {
    display: block;
  }

  /* Compose score bar */
  .compose-score {
    font-size: 12px;
    color: var(--text2);
    font-variant-numeric: tabular-nums;
  }
  .compose-bar {
    height: 3px;
    border-radius: 2px;
    background: var(--border);
    margin-top: 3px;
    overflow: hidden;
  }
  .compose-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: var(--accent);
    transition: width 0.3s ease;
  }

  /* Empty state */
  .empty {
    text-align: center;
    padding: 80px 20px;
    color: var(--text2);
  }
  .empty p { font-size: 15px; }

  /* Search */
  .search-input {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    color: var(--text);
    font-size: 13px;
    width: 200px;
    outline: none;
    transition: border-color 0.15s;
  }
  .search-input::placeholder { color: var(--text2); }
  .search-input:focus { border-color: var(--accent); }

  /* Responsive */
  @media (max-width: 768px) {
    .header, .toolbar, .table-wrap { padding-left: 16px; padding-right: 16px; }
    .toolbar { gap: 8px; }
    .search-input { width: 140px; }
    .hide-mobile { display: none; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>Idea <span>Stream</span></h1>
  <div class="sub" id="subtitle">Research paper feed for embodied AI &amp; visual intelligence</div>
</div>

<div class="toolbar">
  <div class="sort-group">
    <label>Sort</label>
    <button class="pill-btn active" data-sort="must_read">Must Read <span class="algo-tag">Q+R+T</span></button>
    <button class="pill-btn" data-sort="discovery">Discovery <span class="algo-tag">R+T</span></button>
    <button class="pill-btn" data-sort="quality">Quality</button>
    <button class="pill-btn" data-sort="relevance">Relevance</button>
    <button class="pill-btn" data-sort="date">Date</button>
  </div>

  <div style="width:1px;height:24px;background:var(--border);margin:0 4px;" class="hide-mobile"></div>

  <div class="filter-group">
    <label>Topic</label>
    <button class="pill-btn active" data-topic="all">All</button>
    <span id="topic-buttons"></span>
  </div>

  <div class="spacer"></div>

  <input type="text" class="search-input" id="search" placeholder="Search titles..." />

  <div class="stat"><b id="count">0</b> papers</div>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th class="center" style="width:40px">#</th>
        <th>Paper</th>
        <th class="center hide-mobile" style="width:90px">Quality</th>
        <th class="center hide-mobile" style="width:90px">Relevance</th>
        <th class="center hide-mobile" style="width:100px" id="compose-header">Must Read</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
  <div class="empty" id="empty" style="display:none;">
    <p>No papers match your filters.</p>
  </div>
</div>

<script>
const PAPERS = __PAPERS__;
const TOPICS = __TOPICS__;
const SORT_KEY = "__SORT__";

let currentSort = "must_read";
let currentTopic = "all";
let searchTerm = "";

// --- topic buttons ---
const topicContainer = document.getElementById("topic-buttons");
TOPICS.forEach(t => {
  const btn = document.createElement("button");
  btn.className = "pill-btn";
  btn.dataset.topic = t.topic;
  btn.textContent = t.topic + " (" + t.count + ")";
  topicContainer.appendChild(btn);
});

// --- scoring (mirrors Python) ---
function daysAgo(dateStr) {
  const parts = dateStr.split("-");
  const paper = new Date(+parts[0], +parts[1]-1, +parts[2]);
  const now = new Date(2026, 4, 18);
  return Math.max((now - paper) / 86400000, 0);
}

function mustReadScore(p) {
  const geo = Math.sqrt(p.quality_score * p.relevance_score);
  const recency = 1.0 + 0.4 * Math.exp(-daysAgo(p.paper_date) / 120);
  return geo * recency;
}

function discoveryScore(p) {
  const rel = Math.pow(p.relevance_score, 1.3);
  const recency = 1.0 + 0.8 * Math.exp(-daysAgo(p.paper_date) / 60);
  const qual = 1.0 + 0.15 * p.quality_score;
  return rel * recency * qual;
}

const sortFns = {
  quality:    (a, b) => b.quality_score - a.quality_score || b.relevance_score - a.relevance_score,
  relevance:  (a, b) => b.relevance_score - a.relevance_score || b.quality_score - a.quality_score,
  date:       (a, b) => b.paper_date.localeCompare(a.paper_date) || b.relevance_score - a.relevance_score,
  must_read:  (a, b) => mustReadScore(b) - mustReadScore(a),
  discovery:  (a, b) => discoveryScore(b) - discoveryScore(a),
};

const scoreFns = {
  must_read: mustReadScore,
  discovery: discoveryScore,
};

const composeLabels = {
  must_read: "Must Read",
  discovery: "Discovery",
};

function qClass(s) { return s >= 8 ? "q-high" : s >= 6 ? "q-mid" : "q-low"; }
function rClass(s) { return s >= 8 ? "r-high" : s >= 6 ? "r-mid" : "r-low"; }

function render() {
  let papers = PAPERS.slice();
  if (currentTopic !== "all") papers = papers.filter(p => p.topic === currentTopic);
  if (searchTerm) {
    const lower = searchTerm.toLowerCase();
    papers = papers.filter(p =>
      p.title.toLowerCase().includes(lower) ||
      p.id.toLowerCase().includes(lower)
    );
  }
  papers.sort(sortFns[currentSort]);

  const composeHeader = document.getElementById("compose-header");
  composeHeader.textContent = composeLabels[currentSort] || "Score";

  const tbody = document.getElementById("tbody");
  const empty = document.getElementById("empty");
  document.getElementById("count").textContent = papers.length;

  if (papers.length === 0) {
    tbody.innerHTML = "";
    empty.style.display = "";
    return;
  }
  empty.style.display = "none";

  const scoreFn = scoreFns[currentSort];
  let maxCompose = 1;
  if (scoreFn) {
    maxCompose = Math.max(...papers.map(scoreFn));
  }

  tbody.innerHTML = papers.map((p, i) => {
    const composeVal = scoreFn ? scoreFn(p) : null;
    const composePct = composeVal != null ? Math.round(composeVal / maxCompose * 100) : null;
    const composeHtml = composeVal != null
      ? `<td class="center hide-mobile">
           <div class="compose-score">${composeVal.toFixed(2)}</div>
           <div class="compose-bar"><div class="compose-bar-fill" style="width:${composePct}%"></div></div>
         </td>`
      : `<td class="center hide-mobile"><span style="color:var(--text2);">-</span></td>`;

    return `<tr>
      <td class="center"><span class="rank">${i + 1}</span></td>
      <td class="title-cell">
        <a href="${p.link}" target="_blank" rel="noopener">${esc(p.title)}</a>
        <div class="title-meta">
          <span class="tag tag-${p.topic}">${p.topic}</span>
          <span class="date">${p.paper_date}</span>
        </div>
      </td>
      <td class="center hide-mobile">
        <div class="reason-wrap">
          <span class="score-badge ${qClass(p.quality_score)}">${p.quality_score}</span>
          <div class="reason-tip">${esc(p.quality_reason)}</div>
        </div>
      </td>
      <td class="center hide-mobile">
        <div class="reason-wrap">
          <span class="score-badge ${rClass(p.relevance_score)}">${p.relevance_score}</span>
          <div class="reason-tip">${esc(p.relevance_reason)}</div>
        </div>
      </td>
      ${composeHtml}
    </tr>`;
  }).join("");
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

// --- event handlers ---
document.querySelectorAll("[data-sort]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-sort]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentSort = btn.dataset.sort;
    render();
  });
});

document.querySelectorAll("[data-topic]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-topic]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentTopic = btn.dataset.topic;
    render();
  });
});

document.getElementById("search").addEventListener("input", e => {
  searchTerm = e.target.value;
  render();
});

render();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/papers":
            topic = params.get("topic", [None])[0]
            sort = params.get("sort", ["must_read"])[0]
            papers = fetch_papers(topic)
            if sort in SORT_FNS:
                papers = SORT_FNS[sort](papers)
            self._json(papers)
        elif parsed.path == "/api/topics":
            self._json(get_topics())
        elif parsed.path == "/" or parsed.path == "":
            page = HTML_PAGE
            page = page.replace("__PAPERS__", json.dumps(fetch_papers()))
            page = page.replace("__TOPICS__", json.dumps(get_topics()))
            page = page.replace("__SORT__", "must_read")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # quiet


if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Idea Stream running at http://localhost:{port}")
    server.serve_forever()
