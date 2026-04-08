# 🕸️ 线索网 (Clue Web) — OSINT Investigation Platform

> **Sherlock** 🔍 + **GitNexus** 🕷️ = **线索网** — a visual OSINT investigation tool that maps digital footprints across 400+ platforms into an interactive spider-web intelligence board.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Sherlock v0.16.0](https://img.shields.io/badge/sherlock-v0.16.0_patched-brightgreen)](https://github.com/sherlock-project/sherlock)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

**Language / 语言 / 言語 / 語言 / Bahasa:**

[🇬🇧 English](#english) · [🇨🇳 简体中文](#简体中文) · [🇹🇼 繁體中文](#繁體中文) · [🇯🇵 日本語](#日本語) · [🇲🇾 Bahasa Melayu](#bahasa-melayu)

---

<a name="english"></a>
## 🇬🇧 English

### What Is This?

This is a **forked and enhanced** version of [Sherlock](https://github.com/sherlock-project/sherlock) — the well-known username OSINT tool. On top of the original Sherlock functionality, this fork adds:

1. **9 Critical Bug Fixes** — identified through reverse-engineering the original codebase with [GitNexus](https://gitnexus.dev) code intelligence
2. **线索网 (Clue Web)** — a full-featured investigation visualization tool that generates interactive HTML investigation boards, inspired by GitNexus's spider-web graph interface

### How GitNexus and Sherlock Work Together

| Component | Role |
|-----------|------|
| **GitNexus** | Code intelligence engine used to reverse-engineer Sherlock's call graph, trace execution flows, and identify 9 bugs across 3 files. Its spider-web visualization inspired the Clue Web UI design. |
| **Sherlock** (patched) | The core username enumeration engine — checks 400+ platforms for username existence. This fork includes all 9 bug fixes. |
| **线索网 (Clue Web)** | The investigation visualization layer — takes Sherlock's output and renders it as an interactive node graph with zoom, pan, filtering, depth impact coloring, and per-node context panels. |

### Bug Fixes Applied (9 Total)

| # | Severity | File | Description |
|---|----------|------|-------------|
| 1 | **CRITICAL** | `sherlock.py` | `errorType` list/string inconsistency — sites with list-type `errorType` were silently using wrong HTTP method. Fixed: normalized to list before checks. (+29 extra platforms detected) |
| 2 | **CRITICAL** | `sherlock.py` | `response_text = r.text.encode()` caused bytes/str mismatch in all downstream string comparisons. Fixed: removed `.encode()`. |
| 3 | **BUG** | `notify.py` | Off-by-one in `finish()` — called `countResults()-1` instead of `getResults()`. |
| 4 | **MEDIUM** | `notify.py` | Thread-unsafe global counter (`globvar`). Replaced with `threading.Lock()` + `_results_count`. |
| 5 | **MEDIUM** | `sites.py` | Mutable default argument `do_not_exclude=[]`. Fixed with `None` default + guard. |
| 6 | **MEDIUM** | `sites.py` | `username_unclaimed` always overwritten by random token. Fixed: use passed value if not `None`. |
| 7 | **MEDIUM** | `sherlock.py` | `--no-print-found` argparse logic inverted. Fixed `action="store_false"`. |
| 8 | **MEDIUM** | `sherlock.py` | WAF detection crashed when `response` was `None`. Added null guard. |
| 9 | **MINOR** | `sherlock.py` | Version strip used `.lstrip("v")` which also strips characters like `r`, `e`. Fixed with proper prefix removal. |

### Clue Web Features (GitNexus-Inspired)

The generated HTML investigation board has **full feature parity** with GitNexus's graph interface:

| Feature | Description |
|---------|-------------|
| **Zoom & Pan** | Mouse wheel to zoom, right-click drag to pan |
| **Node Drag** | Left-click drag any node to reposition |
| **Depth Impact Coloring** | BFS from selected node: d=1 bright → d=2 medium → d=3+ dim (like GitNexus blast radius) |
| **Context Panel** | Click any node → right panel shows 360° view per type (TARGET / VARIANT / CATEGORY / SITE) |
| **Variant Filter** | Click a username variant in the left panel → isolates only that variant's found platforms |
| **Category Toggles** | Show/hide entire categories (Social, Gaming, Tech, Creative, Finance, Forums, Academic, Other) |
| **Real-Time Search** | Type in the search bar to dim non-matching nodes |
| **Minimap** | Bottom-right minimap with viewport rectangle — click to teleport |
| **Breadcrumb** | Bottom bar shows clickable navigation path: Target → Variant → Category → Site |
| **Export** | One-click copy all discovered URLs to clipboard |
| **Keyboard Shortcuts** | `R` = fit view, `Esc` = deselect, `+/-` = zoom, double-click = reset |
| **View Modes** | Web (default) / Radial / Focus layouts |
| **Animated Edges** | Particle animation on highlighted/selected connections |

### Quick Start

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

### Output

```
══════════════════════════════════════════════════════════════
  线索网  ·  Clue Web Investigation
══════════════════════════════════════════════════════════════
  Target     : sleepy_lemonade
  Variations : sleepy_lemonade, sleepylemonade, sleepy.lemonade, ...
  Timeout    : 15s / site
──────────────────────────────────────────────────────────────
  [1/8] 'sleepy_lemonade'      →  89 found   (42s)
  [2/8] 'sleepylemonade'       →  74 found   (38s)
  ...
──────────────────────────────────────────────────────────────
  Unique platforms : 242
  Total elapsed    : 285s
══════════════════════════════════════════════════════════════

  Clue web → sleepy_lemonade_clue_web.html
```

The HTML file opens automatically in your browser, showing the full investigation board.

### Project Structure

```
sherlock/
├── investigate.py              # 线索网 investigation runner (NEW)
├── clue_web_template.html      # GitNexus-style visualization template (NEW)
├── sherlock_project/
│   ├── sherlock.py             # Core engine (5 bugs fixed)
│   ├── notify.py               # Result notification (2 bugs fixed)
│   ├── sites.py                # Site definitions (2 bugs fixed)
│   └── resources/
│       └── data.json           # 400+ platform definitions
├── README.md                   # This file (multilingual)
└── <username>_clue_web.html    # Generated investigation boards
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `username` | (required) | Target username to investigate |
| `--timeout` | `10` | Timeout per site in seconds |
| `--max-variations` | `8` | Maximum username variations to generate |
| `--no-browser` | `false` | Don't auto-open the HTML result |

### Username Variation Engine

The tool automatically generates variations of the target username:

| Input | Variations Generated |
|-------|---------------------|
| `sleepy_lemonade` | `sleepy_lemonade`, `sleepylemonade`, `sleepy.lemonade`, `sleepy-lemonade`, `sleepyLemonade`, `SleepyLemonade`, `lemonade_sleepy`, `lemonadesleepy` |

Each variation is searched across 400+ platforms, results are deduplicated, and the combined findings are visualized in the Clue Web.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 什么是线索网？

这是 [Sherlock](https://github.com/sherlock-project/sherlock) 的**增强分叉版本** — 著名的用户名 OSINT (开源情报) 工具。在原版 Sherlock 基础上，本分叉增加了：

1. **9个关键Bug修复** — 通过 [GitNexus](https://gitnexus.dev) 代码智能引擎逆向工程原始代码库发现
2. **线索网 (Clue Web)** — 全功能调查可视化工具，生成交互式 HTML 调查看板，灵感来自 GitNexus 的蛛网图界面

### GitNexus 和 Sherlock 如何协同工作

| 组件 | 作用 |
|------|------|
| **GitNexus** | 代码智能引擎，用于逆向工程 Sherlock 的调用图、跟踪执行流程，并识别3个文件中的9个Bug。其蛛网可视化设计启发了线索网的 UI。 |
| **Sherlock** (已修补) | 核心用户名枚举引擎 — 检查400+平台上的用户名是否存在。本分叉包含所有9个Bug修复。 |
| **线索网** | 调查可视化层 — 获取 Sherlock 的输出并将其渲染为交互式节点图，具有缩放、平移、筛选、深度影响着色和每节点上下文面板。 |

### 快速开始

```bash
# 克隆本分叉
git clone https://github.com/verysleepylemon/sherlock.git
cd sherlock

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -e .

# 运行调查
python investigate.py 用户名
python investigate.py sleepy_lemonade --timeout 20
```

### 线索网功能

| 功能 | 说明 |
|------|------|
| **缩放和平移** | 鼠标滚轮缩放，右键拖动平移 |
| **节点拖拽** | 左键拖动任意节点重新定位 |
| **深度影响着色** | 从选中节点 BFS：d=1 明亮 → d=2 中等 → d=3+ 暗淡 |
| **上下文面板** | 点击任意节点 → 右侧面板显示360°视图 |
| **变体筛选** | 点击左侧用户名变体 → 仅显示该变体找到的平台 |
| **分类开关** | 显示/隐藏整个分类（社交、游戏、科技、创意等） |
| **实时搜索** | 在搜索栏输入，非匹配节点变暗 |
| **小地图** | 右下角小地图，点击传送 |
| **面包屑导航** | 底栏显示可点击路径：目标 → 变体 → 分类 → 站点 |
| **导出** | 一键复制所有已发现的 URL |
| **快捷键** | `R` = 适应视图, `Esc` = 取消选择, `+/-` = 缩放 |

### 修复的9个Bug

| # | 严重性 | 文件 | 描述 |
|---|--------|------|------|
| 1 | **严重** | `sherlock.py` | `errorType` 列表/字符串不一致 — 静默使用了错误的HTTP方法 (+29个额外平台被检测到) |
| 2 | **严重** | `sherlock.py` | `response_text` 的 bytes/str 不匹配 |
| 3 | **Bug** | `notify.py` | `finish()` 中的偏移错误 |
| 4 | **中等** | `notify.py` | 线程不安全的全局计数器 |
| 5 | **中等** | `sites.py` | 可变默认参数 |
| 6 | **中等** | `sites.py` | `username_unclaimed` 总是被随机令牌覆盖 |
| 7 | **中等** | `sherlock.py` | `--no-print-found` argparse 逻辑反转 |
| 8 | **中等** | `sherlock.py` | WAF 检测在响应为 None 时崩溃 |
| 9 | **次要** | `sherlock.py` | 版本前缀剥离不正确 |

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 什麼是線索網？

這是 [Sherlock](https://github.com/sherlock-project/sherlock) 的**增強分叉版本** — 著名的使用者名稱 OSINT（開源情報）工具。在原版 Sherlock 基礎上，本分叉增加了：

1. **9個關鍵Bug修復** — 透過 [GitNexus](https://gitnexus.dev) 程式碼智慧引擎逆向工程原始程式碼庫發現
2. **線索網 (Clue Web)** — 全功能調查視覺化工具，產生互動式 HTML 調查看板，靈感來自 GitNexus 的蛛網圖介面

### GitNexus 和 Sherlock 如何協同運作

| 元件 | 作用 |
|------|------|
| **GitNexus** | 程式碼智慧引擎，用於逆向工程 Sherlock 的呼叫圖、追蹤執行流程，並識別3個檔案中的9個Bug。其蛛網視覺化設計啟發了線索網的 UI。 |
| **Sherlock**（已修補）| 核心使用者名稱列舉引擎 — 檢查400+平台上的使用者名稱是否存在。本分叉包含所有9個Bug修復。 |
| **線索網** | 調查視覺化層 — 取得 Sherlock 的輸出並將其渲染為互動式節點圖。 |

### 快速開始

```bash
# 複製本分叉
git clone https://github.com/verysleepylemon/sherlock.git
cd sherlock

# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/Mac

# 安裝依賴
pip install -e .

# 執行調查
python investigate.py 使用者名稱
python investigate.py sleepy_lemonade --timeout 20
```

### 線索網功能

| 功能 | 說明 |
|------|------|
| **縮放和平移** | 滑鼠滾輪縮放，右鍵拖動平移 |
| **節點拖曳** | 左鍵拖動任意節點重新定位 |
| **深度影響著色** | 從選中節點 BFS：d=1 明亮 → d=2 中等 → d=3+ 暗淡 |
| **上下文面板** | 點擊任意節點 → 右側面板顯示360°檢視 |
| **變體篩選** | 點擊左側使用者名稱變體 → 僅顯示該變體找到的平台 |
| **分類開關** | 顯示/隱藏整個分類 |
| **即時搜尋** | 在搜尋列輸入，非匹配節點變暗 |
| **小地圖** | 右下角小地圖，點擊傳送 |
| **匯出** | 一鍵複製所有已發現的 URL |
| **快速鍵** | `R` = 配合檢視, `Esc` = 取消選擇, `+/-` = 縮放 |

---

<a name="日本語"></a>
## 🇯🇵 日本語

### 线索网（手がかりウェブ）とは？

これは [Sherlock](https://github.com/sherlock-project/sherlock) の**拡張フォーク版** — 有名なユーザー名 OSINT（オープンソースインテリジェンス）ツールです。オリジナルの Sherlock に加えて、このフォークは以下を追加しています：

1. **9つの重大バグ修正** — [GitNexus](https://gitnexus.dev) コードインテリジェンスエンジンを使用して元のコードベースをリバースエンジニアリングして発見
2. **线索网（Clue Web）** — フル機能の調査可視化ツール。インタラクティブな HTML 調査ボードを生成。GitNexus のスパイダーウェブグラフインターフェースにインスパイアされています。

### GitNexus と Sherlock の連携

| コンポーネント | 役割 |
|----------------|------|
| **GitNexus** | コードインテリジェンスエンジン。Sherlock のコールグラフをリバースエンジニアリングし、実行フローを追跡し、3つのファイルで9つのバグを特定。そのスパイダーウェブ可視化が Clue Web の UI デザインにインスピレーションを与えました。 |
| **Sherlock**（パッチ済み）| コアのユーザー名列挙エンジン — 400以上のプラットフォームでユーザー名の存在を確認。このフォークにはすべての9つのバグ修正が含まれています。 |
| **线索网** | 調査可視化レイヤー — Sherlock の出力をインタラクティブなノードグラフとしてレンダリング。 |

### クイックスタート

```bash
# このフォークをクローン
git clone https://github.com/verysleepylemon/sherlock.git
cd sherlock

# 仮想環境を作成
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/Mac

# 依存関係をインストール
pip install -e .

# 調査を実行
python investigate.py ユーザー名
python investigate.py sleepy_lemonade --timeout 20
```

### 线索网の機能

| 機能 | 説明 |
|------|------|
| **ズームとパン** | マウスホイールでズーム、右クリックドラッグでパン |
| **ノードドラッグ** | 左クリックドラッグで任意のノードを再配置 |
| **深度影響カラーリング** | 選択ノードから BFS：d=1 明るい → d=2 中程度 → d=3+ 暗い |
| **コンテキストパネル** | 任意のノードをクリック → 右パネルに360°ビューを表示 |
| **バリアントフィルター** | 左パネルのユーザー名バリアントをクリック → そのバリアントのプラットフォームのみ表示 |
| **カテゴリトグル** | カテゴリ全体の表示/非表示 |
| **リアルタイム検索** | 検索バーに入力して非一致ノードを暗くする |
| **ミニマップ** | 右下のミニマップ、クリックでテレポート |
| **エクスポート** | ワンクリックですべての発見 URL をクリップボードにコピー |
| **キーボードショートカット** | `R` = フィット, `Esc` = 選択解除, `+/-` = ズーム |

---

<a name="bahasa-melayu"></a>
## 🇲🇾 Bahasa Melayu

### Apa Itu 线索网 (Clue Web)?

Ini adalah **fork yang dipertingkatkan** daripada [Sherlock](https://github.com/sherlock-project/sherlock) — alat OSINT (Perisikan Sumber Terbuka) nama pengguna yang terkenal. Selain fungsi Sherlock asal, fork ini menambah:

1. **9 Pembaikan Bug Kritikal** — dikenal pasti melalui kejuruteraan songsang pangkalan kod asal dengan enjin kecerdasan kod [GitNexus](https://gitnexus.dev)
2. **线索网 (Clue Web)** — alat visualisasi siasatan penuh, menghasilkan papan siasatan HTML interaktif, diilhamkan oleh antara muka graf web labah-labah GitNexus

### Bagaimana GitNexus dan Sherlock Bekerjasama

| Komponen | Peranan |
|----------|---------|
| **GitNexus** | Enjin kecerdasan kod yang digunakan untuk kejuruteraan songsang graf panggilan Sherlock, mengesan aliran pelaksanaan, dan mengenal pasti 9 bug dalam 3 fail. Visualisasi web labah-labahnya memberi inspirasi kepada reka bentuk UI Clue Web. |
| **Sherlock** (ditampal) | Enjin penghitungan nama pengguna teras — memeriksa 400+ platform untuk kewujudan nama pengguna. Fork ini merangkumi semua 9 pembaikan bug. |
| **线索网** | Lapisan visualisasi siasatan — mengambil output Sherlock dan memaparkannya sebagai graf nod interaktif. |

### Mula Pantas

```bash
# Klon fork ini
git clone https://github.com/verysleepylemon/sherlock.git
cd sherlock

# Cipta persekitaran maya
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Linux/Mac

# Pasang kebergantungan
pip install -e .

# Jalankan siasatan
python investigate.py nama_pengguna
python investigate.py sleepy_lemonade --timeout 20
```

### Ciri-ciri 线索网

| Ciri | Penerangan |
|------|------------|
| **Zum dan Seret** | Roda tetikus untuk zum, seret klik kanan untuk menggerakkan |
| **Seret Nod** | Seret klik kiri mana-mana nod untuk mengubah kedudukan |
| **Pewarnaan Kesan Kedalaman** | BFS dari nod terpilih: d=1 cerah → d=2 sederhana → d=3+ malap |
| **Panel Konteks** | Klik mana-mana nod → panel kanan menunjukkan pandangan 360° |
| **Penapis Variasi** | Klik variasi nama pengguna di panel kiri → tunjuk platform variasi itu sahaja |
| **Togol Kategori** | Tunjuk/sembunyi keseluruhan kategori |
| **Carian Masa Nyata** | Taip di bar carian untuk malapkan nod yang tidak sepadan |
| **Peta Mini** | Peta mini kanan bawah, klik untuk teleport |
| **Eksport** | Satu klik salin semua URL yang dijumpai ke papan keratan |
| **Pintasan Papan Kekunci** | `R` = muat pandangan, `Esc` = nyahpilih, `+/-` = zum |

---

## Credits & Acknowledgments

- **[Sherlock Project](https://github.com/sherlock-project/sherlock)** — The original OSINT username enumeration tool by [Siddharth Dushantha](https://github.com/sdushantha) and contributors
- **[GitNexus](https://gitnexus.dev)** — Code intelligence engine whose call graph analysis identified the 9 bugs, and whose spider-web visualization interface inspired the Clue Web UI design
- **线索网 (Clue Web)** investigation layer — Built using GitNexus + Sherlock synergy

## License

This project is a fork of [Sherlock](https://github.com/sherlock-project/sherlock), licensed under the [MIT License](LICENSE).
