# GitNexus Integration

This page documents how [GitNexus](https://gitnexus.dev) code intelligence was used throughout this project — from bug discovery to UI design inspiration.

---

## What Is GitNexus?

GitNexus is a **code intelligence engine** that builds a knowledge graph of your codebase. It indexes symbols (functions, classes, methods), maps their relationships (calls, imports, inheritance), and traces execution flows. It provides:

- **Call graph analysis** — who calls what, and who is called by what
- **Execution flow tracing** — step-by-step traces through business processes
- **Impact analysis** — blast radius when changing a symbol (d=1/d=2/d=3 depth)
- **Spider-web visualization** — interactive graph of code relationships

---

## How GitNexus Was Used

### Phase 1: Reverse Engineering Sherlock

GitNexus indexed Sherlock v0.16.0 (with `npx gitnexus analyze`), creating a graph of 57,351 symbols and 61,646 relationships across the codebase.

#### Bug Discovery via Call Graph

```
gitnexus_query({query: "error type handling"})
→ Found execution flow: request() → check_error_type() → compare()
→ Revealed that errorType could be list OR string (Bug 1)
→ Revealed that response_text was bytes not str (Bug 2)
```

```
gitnexus_context({name: "QueryNotifyPrint"})
→ Showed all callers (multi-threaded request workers)
→ Revealed thread-unsafe global counter (Bug 4)
→ Revealed off-by-one in finish() (Bug 3)
```

```
gitnexus_impact({target: "SitesInformation.__init__", direction: "upstream"})
→ Found all call sites passing do_not_exclude and username_unclaimed
→ Revealed mutable default argument (Bug 5)
→ Revealed unconditional override of passed value (Bug 6)
```

### Phase 2: Impact Analysis Before Fixes

Before applying each bug fix, GitNexus impact analysis verified the blast radius:

```
gitnexus_impact({target: "sherlock", direction: "upstream"})
→ d=1: 12 direct callers (all in sherlock.py main)
→ d=2: 3 indirect (notify.py, sites.py)
→ Risk: MEDIUM — changes are internal to the request loop
```

This ensured fixes were safe to apply without breaking external consumers.

### Phase 3: UI Design Inspiration

GitNexus's visualization interface directly inspired the 线索网 (Clue Web) design:

| GitNexus Feature | Clue Web Adaptation |
|------------------|---------------------|
| Symbol nodes (functions, classes) | Investigation nodes (target, variants, categories, sites) |
| Call graph edges | Connection edges (target→variant→category→site) |
| Cluster grouping by module | Category grouping (Social, Gaming, Tech, etc.) |
| Impact depth coloring (d=1/2/3) | BFS depth coloring from selected node |
| Context panel (360° symbol view) | Context panel (360° node view per type) |
| Zoom/pan/drag canvas | Zoom/pan/drag canvas |
| Search filter | Real-time search filter |
| Minimap | Minimap with teleport |
| Breadcrumb | Breadcrumb navigation |
| Process list (sidebar) | Variant list / Category toggles (sidebar) |

### Phase 4: Post-Fix Verification

After applying all 9 fixes:

```
gitnexus_detect_changes({scope: "all"})
→ Modified: sherlock.py (5 symbols changed)
→ Modified: notify.py (2 symbols changed)
→ Modified: sites.py (2 symbols changed)
→ Status: All changes within expected scope
```

---

## GitNexus Impact Risk Levels

The Clue Web depth coloring was directly mapped from GitNexus's impact risk framework:

| GitNexus Level | Depth | Meaning (Code) | Clue Web Equivalent |
|----------------|-------|-----------------|---------------------|
| **WILL BREAK** | d=1 | Direct callers/importers | Full opacity — direct connections |
| **LIKELY AFFECTED** | d=2 | Indirect dependencies | 60% opacity — secondary connections |
| **MAY NEED TESTING** | d=3 | Transitive dependencies | 30% opacity — tertiary connections |
| **LOW RISK** | d>3 | Far from change | 7% opacity — barely visible |

---

## Tools Used

| GitNexus Tool | Purpose in This Project |
|---------------|------------------------|
| `gitnexus_query` | Found execution flows related to error handling, request processing |
| `gitnexus_context` | 360° view of QueryNotifyPrint, SitesInformation, main() |
| `gitnexus_impact` | Blast radius before modifying sherlock(), __init__(), finish() |
| `gitnexus_detect_changes` | Pre-commit verification of change scope |
| Spider-web graph | Direct design inspiration for Clue Web HTML template |

---

## Synergy Summary

```
GitNexus (Code Intelligence)
    │
    ├── Indexed Sherlock codebase → identified 9 bugs
    ├── Impact analysis → verified fix safety
    ├── Spider-web visualization → inspired Clue Web UI design
    │
    ▼
Sherlock (Patched v0.16.0)
    │
    ├── Core OSINT engine (400+ platforms)
    ├── All 9 bugs fixed → more accurate results
    │
    ▼
线索网 (Clue Web)
    │
    └── Investigation visualization → combines both technologies
        into an interactive intelligence board
```

The result is a tool that leverages:
1. GitNexus's **code analysis capabilities** for quality assurance
2. GitNexus's **visualization paradigm** for the user interface  
3. Sherlock's **OSINT enumeration power** for the data layer

This synergy produces a more reliable and visually powerful investigation platform than either tool alone.
