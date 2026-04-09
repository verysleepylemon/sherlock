# 🕸️ 线索网 (Clue Web) — OSINT Investigation Platform

<p align="center">
  <img src="assets/banner.png" alt="线索网 Banner" width="100%">
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://github.com/sherlock-project/sherlock"><img src="https://img.shields.io/badge/sherlock-v0.16.0_patched-brightgreen" alt="Sherlock v0.16.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <br>
  <a href="https://github.com/verysleepylemon/sherlock/actions/workflows/python-anaconda.yml"><img src="https://github.com/verysleepylemon/sherlock/actions/workflows/python-anaconda.yml/badge.svg" alt="Python Package (Anaconda)"></a>
  <a href="https://github.com/verysleepylemon/sherlock/actions/workflows/pylint.yml"><img src="https://github.com/verysleepylemon/sherlock/actions/workflows/pylint.yml/badge.svg" alt="Pylint"></a>
  <a href="https://github.com/verysleepylemon/sherlock/actions/workflows/regression.yml"><img src="https://github.com/verysleepylemon/sherlock/actions/workflows/regression.yml/badge.svg" alt="Regression Testing"></a>
</p>
<p align="center">
  <strong>Sherlock</strong> 🔍 + <strong>GitNexus</strong> 🕷️ = <strong>线索网</strong><br>
  <em>A visual OSINT investigation tool that maps digital footprints across 400+ platforms<br>into an interactive spider-web intelligence board.</em>
</p>

<p align="center">
  <strong>🌐 README in other languages:</strong><br>
  <a href="README.zh-CN.md">🇨🇳 简体中文</a> ·
  <a href="README.zh-TW.md">🇹🇼 繁體中文</a> ·
  <a href="README.ja.md">🇯🇵 日本語</a> ·
  <a href="README.ms.md">🇲🇾 Bahasa Melayu</a>
</p>---

## Demo

### Terminal Output

<p align="center">
  <img src="assets/demo_terminal.gif" alt="Terminal demo — running investigate.py" width="780">
</p>

### Clue Web Investigation Board

<p align="center">
  <img src="assets/clue_web_ui.png" alt="Clue Web UI — interactive investigation board" width="100%">
</p>

<p align="center"><em>Physics-based floating particle network with water drift, spring connections, platform favicons, and break/reconnect mechanics — inspired by <a href="https://gitnexus.dev">GitNexus</a></em></p>

---

## What Is This?

This is a **forked and enhanced** version of [Sherlock](https://github.com/sherlock-project/sherlock) — the well-known username OSINT tool. On top of the original Sherlock, this fork adds:

1. **9 Bug Fixes** — identified by reverse-engineering the codebase with [GitNexus](https://gitnexus.dev) code intelligence (2 critical, 5 medium, 1 bug, 1 minor)
2. **线索网 (Clue Web)** — a full-featured investigation visualization that generates interactive HTML boards, inspired by GitNexus's spider-web graph

---

## How GitNexus and Sherlock Work Together

| Component | Role |
|-----------|------|
| **GitNexus** | Code intelligence engine — reverse-engineered Sherlock's call graph, traced execution flows, identified 9 bugs across 3 files. Its spider-web visualization inspired the Clue Web UI. |
| **Sherlock** (patched) | Core username enumeration engine — checks 400+ platforms. This fork includes all 9 bug fixes. |
| **线索网 (Clue Web)** | Investigation visualization layer — renders Sherlock's output as an interactive node graph with zoom, pan, filtering, depth coloring, and context panels. |

---

## Quick Start

```bash
# Clone this fork
git clone https://github.com/verysleepylemon/sherlock.git
cd sherlock

# Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run investigation
python investigate.py <username>

# Examples
python investigate.py john_doe
python investigate.py sleepy_lemonade --timeout 20
python investigate.py "my username" --max-variations 6 --no-browser
```

The HTML investigation board opens automatically in your browser.

---

## Clue Web Features (GitNexus-Inspired)

### 🌊 Physics Engine

The Clue Web uses a custom **Canvas 2D verlet integration** physics engine — every node floats, drifts, and connects like objects suspended in water.

| Feature | Description |
|---------|-------------|
| **Water Drift** | Sine-wave flow fields create organic, ocean-like movement across all particles |
| **Spring Connections** | Edges behave as springs (k=0.0003) — stretch, compress, and transmit force between nodes |
| **Break / Reconnect** | Connections snap when pulled beyond 240px and automatically reform when particles drift within 140px |
| **Buoyancy** | Gentle upward force (0.015) keeps the network floating with natural bobbing |
| **Mouse Repulsion** | Cursor pushes nearby particles away (radius 160px, force 0.8) — like dragging your hand through water |
| **Damping** | Velocity damping (0.985) prevents runaway physics while keeping motion alive |

### 🎨 Visual Design

| Feature | Description |
|---------|-------------|
| **Deep Ocean Theme** | Dark teal background with animated caustic light beams and floating plankton particles |
| **Platform Favicons** | Site nodes display real favicons loaded via DuckDuckGo icon API |
| **Node Types** | TARGET (hexagon), VARIANT (circle), CATEGORY (diamond), SITE (circle with favicon) |
| **Connection Fading** | Edges thin and fade as they stretch, visually showing strain before breaking |
| **Category Colors** | Social=#e91e63, Gaming=#9c27b0, Tech=#2196f3, Creative=#ff9800, Finance=#4caf50, Forums=#00bcd4, Academic=#ff7043, Other=#607d8b |

### 🕹️ Interaction

| Feature | Description |
|---------|-------------|
| **Zoom & Pan** | Mouse wheel to zoom, right-click drag to pan |
| **Node Drag** | Left-click drag any node to reposition — physics resumes on release |
| **Context Panel** | Click any node → right sidebar shows detailed breakdown per type |
| **Real-Time Search** | Type to filter/dim non-matching nodes |
| **Export** | One-click copy all found URLs to clipboard |
| **Keyboard Shortcuts** | `R` = fit view, `Esc` = deselect |
| **Physics Toggle** | Pause/resume the physics simulation |

---

## Bug Fixes Applied (9 Total)

| # | Severity | File | Description |
|---|----------|------|-------------|
| 1 | **CRITICAL** | `sherlock.py` | `errorType` list/string inconsistency — sites with list `errorType` silently used wrong HTTP method (+29 extra platforms detected) |
| 2 | **CRITICAL** | `sherlock.py` | `response_text = r.text.encode()` caused bytes/str mismatch in all downstream comparisons |
| 3 | **BUG** | `notify.py` | Off-by-one in `finish()` — `countResults()-1` instead of `getResults()` |
| 4 | **MEDIUM** | `notify.py` | Thread-unsafe global counter. Replaced with `threading.Lock()` |
| 5 | **MEDIUM** | `sites.py` | Mutable default argument `do_not_exclude=[]` |
| 6 | **MEDIUM** | `sites.py` | `username_unclaimed` always overwritten by random token |
| 7 | **MEDIUM** | `sherlock.py` | `--no-print-found` argparse logic inverted |
| 8 | **MEDIUM** | `sherlock.py` | WAF detection crashed on `None` response |
| 9 | **MINOR** | `sherlock.py` | Version strip `.lstrip("v")` too aggressive |

---

## Username Variation Engine

The tool automatically generates alternate forms of the target username:

| Input | Variations Generated |
|-------|---------------------|
| `sleepy_lemonade` | `sleepy_lemonade`, `sleepylemonade`, `sleepy.lemonade`, `sleepy-lemonade`, `sleepyLemonade`, `SleepyLemonade`, `lemonade_sleepy`, `lemonadesleepy` |

Each variation is searched across 400+ platforms, results are deduplicated, and combined findings are visualized in the Clue Web.

---

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `username` | (required) | Target username to investigate |
| `--timeout` | `10` | Timeout per site in seconds |
| `--max-variations` | `8` | Maximum username variations to generate |
| `--no-browser` | `false` | Don't auto-open the HTML result |

---

## Project Structure

```
sherlock/
├── investigate.py              # 线索网 investigation runner
├── clue_web_template.html      # GitNexus-style visualization template
├── assets/
│   ├── banner.png              # Repository banner
│   ├── demo_terminal.gif       # Terminal output demo
│   └── clue_web_ui.png         # UI mockup screenshot
├── sherlock_project/
│   ├── sherlock.py             # Core engine (5 bugs fixed)
│   ├── notify.py               # Result notification (2 bugs fixed)
│   ├── sites.py                # Site definitions (2 bugs fixed)
│   └── resources/
│       └── data.json           # 400+ platform definitions
├── wiki/                       # Detailed documentation
├── README.md                   # English (this file)
├── README.zh-CN.md             # 简体中文
├── README.zh-TW.md             # 繁體中文
├── README.ja.md                # 日本語
└── README.ms.md                # Bahasa Melayu
```

---

## Documentation

| Page | Description |
|------|-------------|
| [Architecture](wiki/Architecture.md) | System architecture, node types, data flow |
| [Bug Fixes Detailed](wiki/Bug-Fixes-Detailed.md) | Deep dive into all 9 bugs |
| [Clue Web UI Guide](wiki/Clue-Web-UI-Guide.md) | Full guide to the investigation board |
| [Username Variation Engine](wiki/Username-Variation-Engine.md) | How variations work |
| [GitNexus Integration](wiki/GitNexus-Integration.md) | How GitNexus was used |
| [FAQ](wiki/FAQ.md) | Frequently Asked Questions |

---

## Credits

- **[Sherlock Project](https://github.com/sherlock-project/sherlock)** — Original OSINT username enumeration tool
- **[GitNexus](https://gitnexus.dev)** — Code intelligence engine: call graph analysis found the 9 bugs, spider-web visualization inspired the Clue Web UI
- **线索网 (Clue Web)** — Built with GitNexus + Sherlock synergy

### Animation System

The Clue Web particle physics engine is built from scratch using **Canvas 2D verlet integration** with spring constraints and water drift forces. Inspired by:

- **[tsParticles](https://particles.js.org/)** — Interactive particle library (visual design inspiration)
- **[Particulate.js](https://particulatejs.org/)** — Verlet physics engine (constraint model inspiration)
- **[DuckDuckGo Icon API](https://icons.duckduckgo.com/)** — CORS-friendly favicon provider for platform node images

## License

This project is a fork of [Sherlock](https://github.com/sherlock-project/sherlock), licensed under the [MIT License](LICENSE).
