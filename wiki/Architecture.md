# Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     investigate.py (Orchestrator)                │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ Variation Engine  │    │  HTML Builder     │                   │
│  │                  │    │                  │                   │
│  │ Input: "john_doe"│    │ Input: results   │                   │
│  │ Output:          │    │ Output: HTML     │                   │
│  │  - john_doe      │    │                  │                   │
│  │  - johndoe       │    │ Injects DATA     │                   │
│  │  - john.doe      │    │ payload into     │                   │
│  │  - john-doe      │    │ template         │                   │
│  │  - johnDoe       │    │                  │                   │
│  │  - JohnDoe       │    │                  │                   │
│  │  - doe_john      │    │                  │                   │
│  │  - doejohn       │    │                  │                   │
│  └──────┬───────────┘    └────────▲─────────┘                   │
│         │                         │                             │
│         ▼                         │                             │
│  ┌──────────────────┐    ┌────────┴─────────┐                   │
│  │ Sherlock Runner   │    │ Result Aggregator │                   │
│  │                  │    │                  │                   │
│  │ Subprocess call  │    │ Dedup by site    │                   │
│  │ per variation    │──▶│ Group by category │                   │
│  │ --local flag     │    │ Track sources    │                   │
│  │ Parse [+] lines  │    │ Count per variant│                   │
│  └──────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘

                              │
                              ▼

┌─────────────────────────────────────────────────────────────────┐
│                 clue_web_template.html (Visualization)          │
│                                                                 │
│  ┌──────┬───────────────────────────────────┬────────────────┐  │
│  │ TOP  │  线索网 │ target │ stats │ search │ export│ fit   │  │
│  ├──────┼───────────────────────────────────┼────────────────┤  │
│  │ LEFT │              CANVAS               │  RIGHT PANEL   │  │
│  │      │                                   │  (Context per  │  │
│  │ Vars │  • HTML5 Canvas                   │   node type)   │  │
│  │      │  • DPR-aware rendering            │                │  │
│  │ Cats │  • World coordinate transform     │  TARGET: bars  │  │
│  │      │  • BFS depth coloring             │  VAR: sites    │  │
│  │ Lgnd │  • Node physics                   │  CAT: list     │  │
│  │      │  • Edge animation                 │  SITE: url     │  │
│  ├──────┴───────────────────────────────────┴────────────────┤  │
│  │ BOTTOM: [breadcrumb path]                 [minimap 160×90]│  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Node Types

| Type | Shape | Color | Size | Description |
|------|-------|-------|------|-------------|
| **TARGET** | Hexagon | Gold `#e6b450` | 30px radius | The investigation target username |
| **VAR** (Variation) | Circle | Blue `#58a6ff` | 14px radius | Each username variation checked |
| **CAT** (Category) | Diamond | Category color | 20px radius | Platform category (Social, Gaming, etc.) |
| **SITE** (Platform) | Circle | Category color | 8px radius | Individual platform where username was found |

## Edge Types

| Connection | Style | Meaning |
|-----------|-------|---------|
| TARGET → VAR | Solid, 1.2px | Target has this variation |
| TARGET → CAT | Solid, 1.5px | Target found in this category |
| CAT → SITE | Solid, 0.8px | Site belongs to this category |
| VAR → SITE | Dashed, 0.4px | This variation found this site (shown only when variant filter active) |

## Data Flow

```
investigate.py
  ├── generate_variations(username) → list[str]
  ├── run_sherlock(variation, timeout) → list[dict]
  │     └── subprocess: python -m sherlock_project.sherlock --local
  │           └── parses stdout for [+] lines
  ├── deduplicate results by site name
  ├── group by category (8 categories via regex rules)
  └── build_html(target, results, elapsed)
        ├── constructs DATA JSON payload
        ├── reads clue_web_template.html
        └── replaces /*%%CLUE_DATA%%*/ with const DATA = {...}
```

## Template Injection

The HTML template contains a placeholder comment:
```javascript
/*%%CLUE_DATA%%*/
```

This is replaced at build time with the actual investigation data:
```javascript
const DATA = {
  target: "sleepy_lemonade",
  variations: ["sleepy_lemonade", "sleepylemonade", ...],
  var_counts: {"sleepy_lemonade": 89, "sleepylemonade": 74, ...},
  categories: {
    "Social": [{site:"TikTok", url:"...", username:"...", sources:["..."]}],
    ...
  },
  total: 242,
  elapsed: 285,
  ts: "2026-04-08 14:30",
  cat_meta: {"Social":{"color":"#e91e63"}, ...}
};
```

## Category System

| Category | Color | Rule (URL pattern matching) |
|----------|-------|-----------------------------|
| Social | `#e91e63` | facebook, instagram, twitter, tiktok, snapchat, etc. |
| Gaming | `#9c27b0` | steam, xbox, playstation, twitch, discord, etc. |
| Tech | `#2196f3` | github, stackoverflow, gitlab, npm, pypi, etc. |
| Creative | `#ff9800` | deviantart, behance, dribbble, soundcloud, etc. |
| Finance | `#4caf50` | paypal, venmo, cashapp, coinbase, etc. |
| Forums | `#00bcd4` | reddit, quora, hackernews, discourse, etc. |
| Academic | `#ff7043` | academia, researchgate, orcid, scholar, etc. |
| Other | `#607d8b` | Everything that doesn't match above patterns |

## Coordinate System

The canvas uses a **world coordinate system** with the target at `(0, 0)`:

```
World space:
  TARGET: (0, 0) — center
  VARs:   radius 90px from center
  CATs:   radius 220px from center  
  SITEs:  radius ~380px from center

Transform: canvas_x = world_x × scale + tx
           canvas_y = world_y × scale + ty

Where tx, ty = pan offset, scale = zoom level
```

HiDPI support: All rendering uses `devicePixelRatio` (DPR) scaling for crisp display on Retina/4K screens.
