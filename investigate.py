#!/usr/bin/env python3
"""
线索网 (Clue Web) — OSINT Username Investigation Tool

Runs username + all name variations through fixed Sherlock v0.16.0,
then generates an interactive spider-web investigation board.

Usage:
    python investigate.py sleepylemonade
    python investigate.py john.doe --timeout 20
    python investigate.py "sleepy lemonade" --max-variations 6
"""

import subprocess, sys, json, re, time, webbrowser, argparse, textwrap
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SHERLOCK_DIR = Path(__file__).parent
TEMPLATE_FILE = Path(__file__).parent / 'clue_web_template.html'

# ─── Category metadata ────────────────────────────────────────────────────────
CAT_META = {
    'Social':   {'color': '#e91e63'},
    'Gaming':   {'color': '#9c27b0'},
    'Tech':     {'color': '#2196f3'},
    'Creative': {'color': '#ff9800'},
    'Finance':  {'color': '#4caf50'},
    'Forums':   {'color': '#00bcd4'},
    'Academic': {'color': '#ff7043'},
    'Other':    {'color': '#607d8b'},
}

CAT_RULES = [
    ('Social',   ['instagram','twitter','facebook','tiktok','snapchat','pinterest',
                  'tumblr','bluesky','mastodon','vk','clubhouse','linkedin','threads',
                  'periscope','plurk','tell','askfm','younow','mewe','ello','flipboard',
                  'weibo','renren','vero','clapper','soop']),
    ('Gaming',   ['steam','xbox','twitch','discord','nintendo','roblox','minecraft',
                  'chess','osu','valorant','runescape','itch.io','kongregate','gaiaonline',
                  'battlenet','epicgames','pokemonshowdown','tetr.io','nitrotype',
                  'wowhead','warframe','star citizen','runescape']),
    ('Tech',     ['github','gitlab','gitea','codeberg','stackoverflow','hackerrank',
                  'hackerearth','codeforces','replit','codesandbox','dev.to','hackmd',
                  'codepen','wakatime','codechef','atcoder','leetcode','bugcrowd',
                  'hackerone','hackster','pentesterlab','virustotal','cryptohack',
                  'asciinema','hackernews','docker','packagist']),
    ('Creative', ['behance','dribbble','artstation','deviantart','soundcloud',
                  'mixcloud','bandcamp','reverbnation','vimeo','flickr','500px',
                  'smugmug','gumroad','patreon','buymeacoffe','ko-fi','audiojungle',
                  'cgtrader','sketchfab','carbonmade','issuu','wattpad','blipfoto',
                  'freesound','airbit','tuna','tenor','gifboard','giphy']),
    ('Finance',  ['venmo','cashapp','paypal','freelancer','fiverr','upwork','kwork',
                  'fl.ru','swapd','topmate']),
    ('Forums',   ['reddit','quora','medium','wordpress','blogger','disqus','forum',
                  'community','discuss','phpbb','wykop','habr','kaskus','jbzd',
                  'diskusjon','gutefrage','gesundheitsfrage','dailykos','buzzfeed',
                  'warrior forum','cracked','bezuzyteczna','igromania','velomania']),
    ('Academic', ['academia.edu','researchgate','scholar','orcid','ssrn','mendeley',
                  'launchpad','slides.com','speakerdeck','hackmd','observablehq']),
]


def categorize(site: str, url: str = '') -> str:
    text = (site + ' ' + url).lower()
    for cat, kws in CAT_RULES:
        for kw in kws:
            if kw in text:
                return cat
    return 'Other'


# ─── Name variation generator ────────────────────────────────────────────────
def generate_variations(username: str) -> list:
    """Generate realistic username format variations used across platforms."""
    base = username.strip()
    seen: set = set()
    out: list = []

    def add(v: str):
        v = v.strip()
        if v and len(v) >= 2 and v.lower() not in seen:
            seen.add(v.lower())
            out.append(v)

    add(base)
    lower = base.lower()
    if lower != base:
        add(lower)

    # Separator swaps
    for sep_from in ['_', '-', '.', ' ']:
        if sep_from in lower:
            for sep_to in ['_', '-', '.', '']:
                if sep_to != sep_from:
                    add(lower.replace(sep_from, sep_to))

    # Split into parts and recombine
    parts = [p for p in re.split(r'[._\-\s]+', lower) if p]
    if len(parts) >= 2:
        add(''.join(parts))
        add('_'.join(parts))
        add('.'.join(parts))
        add('-'.join(parts))
        add(''.join(reversed(parts)))
        add('_'.join(reversed(parts)))

    # CamelCase split
    camel = re.sub(r'([A-Z])', r'_\1', base).strip('_').lower()
    camel_parts = [p for p in camel.split('_') if p]
    if camel_parts != parts and len(camel_parts) >= 2:
        add(''.join(camel_parts))
        add('_'.join(camel_parts))

    return out


# ─── Sherlock runner ─────────────────────────────────────────────────────────
def run_sherlock(username: str, timeout: int = 15) -> list:
    results = []
    cmd = [
        sys.executable, '-m', 'sherlock_project.sherlock',
        '--timeout', str(timeout),
        '--no-color', '--local',
        username
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=str(SHERLOCK_DIR), timeout=timeout * 60
        )
        for line in proc.stdout.splitlines():
            m = re.match(r'\[\+\]\s+(.+?):\s+(https?://\S+)', line)
            if m:
                site = m.group(1).strip()
                url  = m.group(2).strip()
                results.append({
                    'site':     site,
                    'url':      url,
                    'username': username,
                    'category': categorize(site, url),
                })
    except subprocess.TimeoutExpired:
        print(f"  ⏱  Timeout for '{username}'")
    except Exception as e:
        print(f"  ✗  Error: {e}")
    return results


# ─── HTML builder ─────────────────────────────────────────────────────────────
def build_html(target: str, var_results: dict, elapsed: float) -> str:
    # Deduplicate sites, tracking which variations matched each
    merged: dict = {}
    for variant, items in var_results.items():
        for item in items:
            key = item['site'].lower()
            if key not in merged:
                merged[key] = {**item, 'sources': [variant]}
            else:
                if variant not in merged[key]['sources']:
                    merged[key]['sources'].append(variant)

    # Group by category
    cat_map: dict = defaultdict(list)
    for v in merged.values():
        cat_map[v['category']].append(v)

    payload = {
        'target':     target,
        'variations': list(var_results.keys()),
        'var_counts': {k: len(v) for k, v in var_results.items()},
        'categories': {k: list(v) for k, v in cat_map.items()},
        'total':      len(merged),
        'elapsed':    round(elapsed, 1),
        'ts':         datetime.now().strftime('%Y-%m-%d %H:%M'),
        'cat_meta':   CAT_META,
    }

    data_js = json.dumps(payload, ensure_ascii=False)
    tpl = TEMPLATE_FILE.read_text(encoding='utf-8')
    return tpl.replace('/*%%CLUE_DATA%%*/', f'const DATA = {data_js};')


# ─── HTML Template ────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>线索网 — Clue Web</title>
<!--NEW_TEMPLATE_V2-->
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0d14; font-family:'Segoe UI','Helvetica Neue',sans-serif; color:#c9d1d9; overflow:hidden; }
#wrap { position:relative; width:100vw; height:100vh; }
canvas { position:absolute; top:0; left:0; }

/* ── Header ── */
#hdr {
  position:absolute; top:0; left:0; right:0; height:52px;
  background:#0d1117cc; border-bottom:1px solid #21262d;
  display:flex; align-items:center; padding:0 18px; z-index:20;
  backdrop-filter:blur(10px); gap:12px;
}
#hdr-badge {
  font-size:13px; font-weight:700; letter-spacing:2px; color:#e6b450;
  text-transform:uppercase; white-space:nowrap;
}
#hdr-sep { width:1px; height:24px; background:#30363d; }
#hdr-target { font-size:17px; font-weight:700; color:#f0f6fc; }
#hdr-sub { font-size:11px; color:#484f58; margin-left:4px; }
#hdr-stats { display:flex; gap:8px; margin-left:auto; }
.spill {
  background:#161b22; border:1px solid #30363d; border-radius:16px;
  padding:3px 10px; font-size:11px; color:#8b949e; white-space:nowrap;
}
.spill b { color:#e6b450; font-weight:700; }

/* ── Sidebar ── */
#sidebar {
  position:absolute; top:52px; right:0; bottom:0; width:232px;
  background:#0d1117ee; border-left:1px solid #21262d;
  overflow-y:auto; z-index:15; padding-bottom:8px;
}
#sidebar::-webkit-scrollbar { width:3px; }
#sidebar::-webkit-scrollbar-thumb { background:#30363d; border-radius:2px; }
.sb-head {
  padding:8px 12px 4px; font-size:10px; font-weight:700; letter-spacing:1px;
  text-transform:uppercase; color:#484f58; border-bottom:1px solid #21262d;
  position:sticky; top:0; background:#0d1117; z-index:1;
}
.cat-block { padding:4px 0 2px; }
.cat-lbl {
  padding:5px 12px; font-size:10px; font-weight:700; letter-spacing:0.5px;
  text-transform:uppercase; display:flex; align-items:center; gap:6px; cursor:default;
}
.cat-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.cat-n { margin-left:auto; font-size:9px; color:#484f58; font-weight:400; }
.sb-item {
  padding:3px 12px 3px 24px; font-size:11px; color:#8b949e; cursor:pointer;
  display:flex; align-items:center; gap:4px; transition:all 0.1s;
  white-space:nowrap; overflow:hidden;
}
.sb-item:hover { color:#c9d1d9; background:#161b2233; }
.sb-item .sb-src {
  font-size:8px; color:#30363d; border:1px solid #30363d; border-radius:3px;
  padding:1px 3px; flex-shrink:0; margin-left:auto; font-family:monospace;
}
.sb-item:hover .sb-src { color:#484f58; border-color:#484f58; }

/* ── Tooltip ── */
#tip {
  position:fixed; z-index:40; background:#161b22f2; border:1px solid #30363d;
  border-radius:8px; padding:11px 14px; max-width:260px; font-size:12px;
  line-height:1.55; pointer-events:none; opacity:0; transition:opacity 0.12s;
  box-shadow:0 8px 32px #00000099;
}
.tn { font-size:13px; font-weight:700; margin-bottom:3px; }
.tc { font-size:10px; opacity:0.7; margin-bottom:3px; }
.tu { font-size:10px; color:#8b949e; word-break:break-all; }
.ts { font-size:10px; color:#58a6ff; margin-top:4px; }
.th { font-size:10px; color:#3fb950; margin-top:3px; }

/* ── Legend ── */
#legend {
  position:absolute; bottom:18px; left:16px; z-index:15;
  display:flex; flex-direction:column; gap:5px;
}
.leg { display:flex; align-items:center; gap:7px; font-size:10px; color:#484f58; }
.leg-s { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.leg-h { width:10px; height:10px; flex-shrink:0; }

/* ── Variant pills ── */
#var-bar {
  position:absolute; bottom:18px; left:50%; transform:translateX(-50%);
  z-index:15; display:flex; gap:5px; flex-wrap:wrap; justify-content:center;
  max-width:600px;
}
.vpill {
  padding:4px 10px; border-radius:14px; font-size:10px; font-family:monospace;
  border:1px solid #30363d; color:#8b949e; background:#0d1117; cursor:pointer;
  transition:all 0.12s; white-space:nowrap;
}
.vpill:hover { color:#58a6ff; border-color:#58a6ff88; background:#1f6feb11; }
.vpill.act  { color:#58a6ff; border-color:#58a6ff; background:#1f6feb22; }
.vpill .vc  { color:#e6b450; margin-left:4px; }
</style>
</head>
<body>
<div id="wrap">
  <canvas id="bgc"></canvas>
  <canvas id="mc"></canvas>

  <div id="hdr">
    <div id="hdr-badge">线索网</div>
    <div id="hdr-sep"></div>
    <div id="hdr-target"></div>
    <div id="hdr-sub"></div>
    <div id="hdr-stats">
      <div class="spill">Platforms <b id="st-total">-</b></div>
      <div class="spill">Categories <b id="st-cats">-</b></div>
      <div class="spill">Variants <b id="st-vars">-</b></div>
      <div class="spill">Elapsed <b id="st-time">-</b></div>
      <div class="spill" style="color:#484f58" id="st-ts"></div>
    </div>
  </div>

  <div id="sidebar">
    <div class="sb-head">Found accounts</div>
  </div>

  <div id="tip"></div>

  <div id="legend">
    <svg width="10" height="10" style="margin-right:5px;display:inline" id="hex-legend"></svg>
    <div class="leg"><canvas id="lc-target" width="10" height="10" style="border-radius:1px"></canvas>Target</div>
    <div class="leg"><div class="leg-s" style="background:#58a6ff;box-shadow:0 0 5px #1f6feb66"></div>Variation</div>
    <div class="leg"><div class="leg-s" style="background:#3fb950;box-shadow:0 0 5px #3fb95066"></div>Category node</div>
    <div class="leg"><div class="leg-s" style="background:#8b949e"></div>Platform (click to open)</div>
  </div>

  <div id="var-bar"></div>
</div>

<script>
/*%%CLUE_DATA%%*/

// ── Constants ────────────────────────────────────────────────────────────────
const HDR = 52;
const SB  = 232;
const NT  = { TARGET:'target', VAR:'var', CAT:'cat', SITE:'site' };

// ── State ────────────────────────────────────────────────────────────────────
let nodes = [], edges = [], nodeMap = {};
let hovered = null, activeVar = null, pulseT = 0;
const bgC = document.getElementById('bgc');
const mc  = document.getElementById('mc');
const bgX = bgC.getContext('2d');
const ctx = mc.getContext('2d');
let DPR = devicePixelRatio || 1;

// ── Dimensions ───────────────────────────────────────────────────────────────
const VW  = () => window.innerWidth;
const VH  = () => window.innerHeight;
const CX  = () => (VW() - SB) / 2;       // canvas center x
const CY  = () => HDR + (VH() - HDR) / 2; // canvas center y
const SD  = () => Math.min(VW() - SB, VH() - HDR); // short dim

// ── Graph builder ────────────────────────────────────────────────────────────
function buildGraph() {
  nodes = []; edges = [];

  const sd   = SD();
  const R_V  = sd * 0.11;  // variation ring
  const R_C  = sd * 0.26;  // category ring
  const R_S  = sd * 0.43;  // site ring

  // Target
  nodes.push({ id:'#target', type:NT.TARGET, label:DATA.target,
    sub:`${DATA.total} found`, x:CX(), y:CY(), r:34,
    color:'#e6b450', glow:'#e6b45055', url:null, cat:null, sources:[] });

  // Variations
  const vars = DATA.variations;
  vars.forEach((v, i) => {
    const a = (i / vars.length) * Math.PI * 2 - Math.PI / 2;
    const cnt = DATA.var_counts[v] || 0;
    nodes.push({ id:`$v:${v}`, type:NT.VAR, label:v,
      sub:`${cnt}`, x:CX() + Math.cos(a)*R_V, y:CY() + Math.sin(a)*R_V,
      r:12, color:'#58a6ff', glow:'#1f6feb33', url:null, cat:null, sources:[], variant:v });
    edges.push({ from:'#target', to:`$v:${v}`, w:0.8, col:'#58a6ff55', dash:false });
  });

  // Categories (only those with results)
  const catKeys = Object.keys(DATA.categories)
    .filter(k => DATA.categories[k].length > 0)
    .sort((a,b) => DATA.categories[b].length - DATA.categories[a].length);

  const catAngles = {};
  catKeys.forEach((cat, i) => {
    const a = (i / catKeys.length) * Math.PI * 2 - Math.PI / 2;
    catAngles[cat] = a;
    const meta = DATA.cat_meta[cat] || { color:'#607d8b' };
    nodes.push({ id:`$c:${cat}`, type:NT.CAT, label:cat,
      sub:`${DATA.categories[cat].length}`, x:CX() + Math.cos(a)*R_C, y:CY() + Math.sin(a)*R_C,
      r:18, color:meta.color, glow:meta.color+'33', url:null, cat:cat, sources:[] });
    edges.push({ from:'#target', to:`$c:${cat}`, w:1.5, col:meta.color+'33', dash:false });
  });

  // Sites — grouped in arcs around their category
  catKeys.forEach(cat => {
    const sites = DATA.categories[cat];
    const baseA  = catAngles[cat];
    const meta   = DATA.cat_meta[cat] || { color:'#607d8b' };
    const maxSpread = Math.PI * 0.6;
    const spread = Math.min(maxSpread, Math.max(0.28, sites.length * 0.13));

    sites.forEach((site, idx) => {
      const t  = sites.length === 1 ? 0.5 : idx / (sites.length - 1);
      const a  = baseA + (t - 0.5) * spread;
      const rj = R_S + (idx % 3 - 1) * 14; // radial stagger
      const nid = `$s:${site.site}`;
      nodes.push({ id:nid, type:NT.SITE, label:site.site,
        sub:'', x:CX() + Math.cos(a)*rj, y:CY() + Math.sin(a)*rj,
        r:9, color:meta.color, glow:meta.color+'22', url:site.url,
        cat:cat, sources:site.sources || [], username:site.username });
      edges.push({ from:`$c:${cat}`, to:nid, w:0.7, col:meta.color+'88', dash:false });
    });
  });

  nodeMap = {};
  nodes.forEach(n => nodeMap[n.id] = n);
}

// ── Resize ───────────────────────────────────────────────────────────────────
function resize() {
  DPR = devicePixelRatio || 1;
  const W = VW(), H = VH();
  [bgC, mc].forEach(c => {
    c.width  = W * DPR; c.height = H * DPR;
    c.style.width = W+'px'; c.style.height = H+'px';
  });
  bgX.setTransform(DPR,0,0,DPR,0,0);
  ctx.setTransform(DPR,0,0,DPR,0,0);
  buildGraph();
  drawBG();
}

// ── Background ───────────────────────────────────────────────────────────────
function drawBG() {
  const W = VW(), H = VH(), cx = CX(), cy = CY(), sd = SD();
  bgX.clearRect(0,0,W,H);

  const g = bgX.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W,H)*0.7);
  g.addColorStop(0,'#0e1520'); g.addColorStop(1,'#0a0d14');
  bgX.fillStyle = g; bgX.fillRect(0,0,W,H);

  // Grid
  bgX.strokeStyle='#ffffff06'; bgX.lineWidth=0.5;
  for (let x=0;x<W;x+=44) { bgX.beginPath();bgX.moveTo(x,0);bgX.lineTo(x,H);bgX.stroke(); }
  for (let y=HDR;y<H;y+=44) { bgX.beginPath();bgX.moveTo(0,y);bgX.lineTo(W,y);bgX.stroke(); }

  // Web rings at each orbital radius
  [0.11, 0.26, 0.43, 0.57].forEach(f => {
    bgX.beginPath(); bgX.arc(cx,cy,sd*f,0,Math.PI*2);
    bgX.strokeStyle='#1f6feb14'; bgX.lineWidth=1; bgX.stroke();
  });

  // Spokes
  for (let i=0;i<12;i++) {
    const a = (i/12)*Math.PI*2;
    bgX.beginPath(); bgX.moveTo(cx,cy);
    bgX.lineTo(cx+Math.cos(a)*sd*0.6, cy+Math.sin(a)*sd*0.6);
    bgX.strokeStyle='#1f6feb0b'; bgX.lineWidth=0.5; bgX.stroke();
  }
}

// ── Hex path ─────────────────────────────────────────────────────────────────
function hexPath(cx,cy,r) {
  ctx.beginPath();
  for (let i=0;i<6;i++) {
    const a = (i/6)*Math.PI*2 - Math.PI/6;
    i===0 ? ctx.moveTo(cx+r*Math.cos(a), cy+r*Math.sin(a))
          : ctx.lineTo(cx+r*Math.cos(a), cy+r*Math.sin(a));
  }
  ctx.closePath();
}

// ── Color utils ──────────────────────────────────────────────────────────────
function alpha(hex, a) {
  return hex + Math.round(a*255).toString(16).padStart(2,'0');
}
function darken(hex, f) {
  hex = hex.replace('#','');
  if (hex.length===3) hex=hex.split('').map(c=>c+c).join('');
  const r = Math.min(255,Math.round(parseInt(hex.slice(0,2),16)*f));
  const g = Math.min(255,Math.round(parseInt(hex.slice(2,4),16)*f));
  const b = Math.min(255,Math.round(parseInt(hex.slice(4,6),16)*f));
  return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
}
function trunc(s,n) { return s.length>n ? s.slice(0,n-1)+'…':s; }

// ── Draw edge ────────────────────────────────────────────────────────────────
function drawEdge(e, hilite) {
  const a = nodeMap[e.from], b = nodeMap[e.to]; if(!a||!b) return;

  // Filter by active variant highlight
  if (activeVar) {
    const sNode = nodeMap[e.to] || nodeMap[e.from];
    const relevant = (e.from===`$v:${activeVar}` || e.to===`$v:${activeVar}` ||
                      (sNode && sNode.sources && sNode.sources.includes(activeVar)));
    if (!relevant) return;
  }

  const opa = hilite ? Math.min(e.col.length>7 ? 1 : 0.9, 1) :
              (hovered ? 0.12 : (activeVar ? 0.4 : 1));

  const gl = ctx.createLinearGradient(a.x,a.y,b.x,b.y);
  const c = e.col.slice(0,7);
  gl.addColorStop(0, alpha(c, opa*0.6));
  gl.addColorStop(1, alpha(c, opa));
  ctx.save();
  ctx.strokeStyle = gl; ctx.lineWidth = hilite ? e.w*2 : e.w;
  if (e.dash) ctx.setLineDash([3,5]);
  ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
  ctx.setLineDash([]); ctx.restore();

  // Animated particles on highlighted edges
  if (hilite) {
    const t = (pulseT * 0.5) % 1;
    const px = a.x+(b.x-a.x)*t, py = a.y+(b.y-a.y)*t;
    ctx.beginPath(); ctx.arc(px,py,2,0,Math.PI*2);
    ctx.fillStyle = c+'cc';
    ctx.shadowColor=c; ctx.shadowBlur=8;
    ctx.fill(); ctx.shadowBlur=0;
  }
}

// ── Draw node ────────────────────────────────────────────────────────────────
function drawNode(n, isH) {
  const { x,y,r,color,glow,type } = n;
  const nr = r + (isH ? 3 : 0);

  // Glow halo
  const gr = ctx.createRadialGradient(x,y,nr*0.2,x,y,nr*(isH?3.2:2.2));
  gr.addColorStop(0, glow); gr.addColorStop(1,'transparent');
  ctx.beginPath(); ctx.arc(x,y,nr*(isH?3.2:2.2),0,Math.PI*2);
  ctx.fillStyle=gr; ctx.fill();

  // Shape
  ctx.save();
  ctx.shadowColor=color+(isH?'aa':'55');
  ctx.shadowBlur=isH?18:10;

  if (type===NT.TARGET) hexPath(x,y,nr);
  else { ctx.beginPath(); ctx.arc(x,y,nr,0,Math.PI*2); }

  const bg=ctx.createRadialGradient(x,y-nr*0.3,nr*0.1,x,y,nr);
  bg.addColorStop(0,darken(color,0.65)+'ff');
  bg.addColorStop(1,darken(color,0.45)+'dd');
  ctx.fillStyle=bg; ctx.fill();

  ctx.strokeStyle=color+(isH?'ff':'cc');
  ctx.lineWidth=isH?2:1.5; ctx.stroke();

  // Inner ring for category  
  if (type===NT.CAT) {
    ctx.beginPath(); ctx.arc(x,y,nr-5,0,Math.PI*2);
    ctx.strokeStyle=color+'22'; ctx.lineWidth=1; ctx.stroke();
  }
  ctx.restore();

  // Labels
  ctx.textAlign='center'; ctx.textBaseline='middle';
  if (type===NT.TARGET) {
    ctx.fillStyle=color;
    ctx.font=`bold 12px 'Segoe UI',sans-serif`;
    ctx.fillText(trunc(n.label,16),x,y-5);
    ctx.fillStyle=color+'99'; ctx.font=`9px 'Segoe UI',sans-serif`;
    ctx.fillText(n.sub,x,y+7);
  } else if (type===NT.CAT) {
    ctx.fillStyle=color;
    ctx.font=`bold 8px 'Segoe UI',sans-serif`;
    ctx.fillText(trunc(n.label,10),x,y-3);
    ctx.fillStyle=color+'aa'; ctx.font=`7px 'Segoe UI',sans-serif`;
    ctx.fillText(n.sub,x,y+6);
  } else if (type===NT.VAR) {
    ctx.fillStyle=color+'cc';
    ctx.font=`8px 'Segoe UI',monospace`;
    ctx.textBaseline='top';
    ctx.fillText(trunc(n.label,13),x,y+nr+3);
  } else if (type===NT.SITE && isH) {
    ctx.fillStyle=color;
    ctx.font=`bold 9px 'Segoe UI',sans-serif`;
    ctx.textBaseline='top';
    ctx.fillText(trunc(n.label,16),x,y+nr+3);
  }
}

// ── Render loop ───────────────────────────────────────────────────────────────
function render(ts=0) {
  pulseT = ts * 0.001;
  ctx.clearRect(0,0,VW(),VH());

  const hiliteSet = new Set();
  if (hovered) {
    edges.forEach(e => { if(e.from===hovered.id||e.to===hovered.id) hiliteSet.add(e); });
  }

  edges.forEach(e => drawEdge(e, hiliteSet.has(e)));
  nodes.forEach(n => drawNode(n, n===hovered));

  requestAnimationFrame(render);
}

// ── Hit test ─────────────────────────────────────────────────────────────────
function hitTest(mx,my) {
  for (let i=nodes.length-1;i>=0;i--) {
    const n=nodes[i];
    if ((mx-n.x)**2+(my-n.y)**2 <= (n.r+6)**2) return n;
  }
  return null;
}

// ── Tooltip ───────────────────────────────────────────────────────────────────
const tipEl = document.getElementById('tip');
function showTip(n, px, py) {
  const meta = (n.cat && DATA.cat_meta[n.cat]) || {};
  const nc = n.color;
  let html='';
  if (n.type===NT.TARGET) {
    html=`<div class="tn" style="color:${nc}">${n.label}</div>
<div class="tc" style="color:#8b949e">Investigation Target</div>
<div class="tu">${DATA.total} unique platforms · ${DATA.variations.length} variations checked</div>
<div class="ts">Variants: ${DATA.variations.join(', ')}</div>`;
  } else if (n.type===NT.VAR) {
    html=`<div class="tn" style="color:${nc}">${n.label}</div>
<div class="tc" style="color:#8b949e">Username Variation</div>
<div class="tu">${n.sub} platforms found with this variant</div>`;
  } else if (n.type===NT.CAT) {
    html=`<div class="tn" style="color:${nc}">${n.label}</div>
<div class="tc" style="color:#8b949e">Platform Category</div>
<div class="tu">${n.sub} accounts found in this category</div>`;
  } else if (n.type===NT.SITE) {
    html=`<div class="tn" style="color:${nc}">${n.label}</div>
<div class="tc" style="color:${meta.color||nc}">${n.cat}</div>
<div class="tu">${n.url}</div>
<div class="ts">Found via: ${(n.sources||[]).join(', ')}</div>
<div class="th">↗ Click to open</div>`;
  }
  tipEl.innerHTML=html; tipEl.style.opacity='1';
  let tx=px+14, ty=py-10;
  if (tx+270>VW()-SB-10) tx=px-280;
  if (ty+180>VH()) ty=VH()-180;
  if (ty<58) ty=58;
  tipEl.style.left=tx+'px'; tipEl.style.top=ty+'px';
}
function hideTip() { tipEl.style.opacity='0'; }

// ── Events ────────────────────────────────────────────────────────────────────
mc.addEventListener('mousemove', e => {
  const r = mc.getBoundingClientRect();
  const h = hitTest(e.clientX-r.left, e.clientY-r.top);
  if (h!==hovered) { hovered=h; mc.style.cursor=h?(h.url?'pointer':'crosshair'):'default'; }
  h ? showTip(h,e.clientX,e.clientY) : hideTip();
});
mc.addEventListener('click', e => {
  if (hovered && hovered.url) window.open(hovered.url,'_blank');
});
mc.addEventListener('mouseleave', ()=>{ hovered=null; hideTip(); });
window.addEventListener('resize', ()=>{ resize(); drawBG(); });

// ── Sidebar ───────────────────────────────────────────────────────────────────
function buildSidebar() {
  const sb = document.getElementById('sidebar');
  let html = '<div class="sb-head">Found accounts</div>';
  const cats = Object.keys(DATA.categories)
    .filter(k=>DATA.categories[k].length>0)
    .sort((a,b)=>DATA.categories[b].length-DATA.categories[a].length);

  cats.forEach(cat => {
    const sites = DATA.categories[cat];
    const meta  = DATA.cat_meta[cat] || { color:'#607d8b' };
    html += `<div class="cat-block">
<div class="cat-lbl"><div class="cat-dot" style="background:${meta.color}"></div>
<span style="color:${meta.color}">${cat}</span><span class="cat-n">${sites.length}</span></div>`;
    sites.forEach(s => {
      const sid  = `$s:${s.site}`;
      const src  = s.sources&&s.sources[0] ? `<span class="sb-src">${s.sources[0]}</span>` : '';
      html += `<div class="sb-item"
  onclick="window.open('${s.url}','_blank')"
  onmouseenter="sbHover('${sid}')"
  onmouseleave="sbLeave()">${s.site}${src}</div>`;
    });
    html += '</div>';
  });
  sb.innerHTML = html;
}

function sbHover(id) { hovered = nodeMap[id]||null; }
function sbLeave()   { hovered = null; }

// ── Variant pills ─────────────────────────────────────────────────────────────
function buildVarBar() {
  const bar = document.getElementById('var-bar');
  bar.innerHTML = DATA.variations.map(v => {
    const cnt = DATA.var_counts[v]||0;
    return `<div class="vpill" data-v="${v}" onclick="toggleVar('${v}')">
${v}<span class="vc">${cnt}</span></div>`;
  }).join('');
}

function toggleVar(v) {
  activeVar = activeVar===v ? null : v;
  document.querySelectorAll('.vpill').forEach(el => {
    el.classList.toggle('act', el.dataset.v===activeVar);
  });
}

// ── Stats bar ─────────────────────────────────────────────────────────────────
function fillStats() {
  document.getElementById('hdr-target').textContent = DATA.target;
  document.getElementById('hdr-sub').textContent = `(${DATA.ts})`;
  document.getElementById('st-total').textContent = DATA.total;
  document.getElementById('st-cats').textContent =
    Object.keys(DATA.categories).filter(k=>DATA.categories[k].length).length;
  document.getElementById('st-vars').textContent = DATA.variations.length;
  document.getElementById('st-time').textContent  = DATA.elapsed+'s';
  document.getElementById('st-ts').textContent   = DATA.ts;
  document.title = `线索网 · ${DATA.target} — ${DATA.total} found`;
}

// ── Boot ──────────────────────────────────────────────────────────────────────
resize();
buildSidebar();
buildVarBar();
fillStats();
requestAnimationFrame(render);
</script>
</body>
</html>
"""

# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog='investigate',
        description='线索网 — OSINT Clue Web: search username variations, visualise as spider web',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          python investigate.py sleepylemonade
          python investigate.py john.doe --timeout 20
          python investigate.py "sleepy lemonade" --max-variations 6 --no-browser
        """)
    )
    parser.add_argument('username',          help='Target username to investigate')
    parser.add_argument('--timeout',   type=int, default=15, help='HTTP timeout per site (default: 15s)')
    parser.add_argument('--max-variations', type=int, default=8,
                        help='Max name variations to check (default: 8)')
    parser.add_argument('--no-browser', action='store_true', help='Do not auto-open the HTML')
    args = parser.parse_args()

    target     = args.username.strip()
    variations = generate_variations(target)[:args.max_variations]

    print(f"\n{'═'*62}")
    print(f"  线索网  ·  Clue Web Investigation")
    print(f"{'═'*62}")
    print(f"  Target     : {target}")
    print(f"  Variations : {', '.join(variations)}")
    print(f"  Timeout    : {args.timeout}s / site")
    print(f"{'─'*62}")

    var_results: dict = {}
    t0 = time.time()

    for i, variant in enumerate(variations, 1):
        print(f"  [{i}/{len(variations)}] {variant!r:<24} ", end='', flush=True)
        ts = time.time()
        results = run_sherlock(variant, args.timeout)
        var_results[variant] = results
        print(f"→  {len(results):>3} found   ({time.time()-ts:.0f}s)")

    elapsed    = time.time() - t0
    all_sites  = {item['site'].lower() for items in var_results.values() for item in items}
    total_uniq = len(all_sites)

    print(f"{'─'*62}")
    print(f"  Unique platforms : {total_uniq}")
    print(f"  Total elapsed    : {elapsed:.0f}s")
    print(f"{'═'*62}")

    html      = build_html(target, var_results, elapsed)
    safe_name = re.sub(r'[^\w.-]', '_', target)
    out_file  = SHERLOCK_DIR / f"{safe_name}_clue_web.html"
    out_file.write_text(html, encoding='utf-8')

    print(f"\n  Clue web → {out_file}")
    if not args.no_browser:
        webbrowser.open(str(out_file))
        print("  Opened in browser.\n")


if __name__ == '__main__':
    main()
