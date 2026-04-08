# 线索网 (Clue Web) Wiki

Welcome to the 线索网 investigation platform documentation.

## Table of Contents

1. [[Home]] — This page
2. [[Architecture]] — How the system is built
3. [[Bug-Fixes-Detailed]] — Deep dive into all 9 bugs found and fixed
4. [[Clue-Web-UI-Guide]] — Full guide to the investigation board interface
5. [[Username-Variation-Engine]] — How username variations are generated
6. [[GitNexus-Integration]] — How GitNexus was used to build this project
7. [[FAQ]] — Frequently Asked Questions

---

## Quick Overview

**线索网 (Clue Web)** is an OSINT investigation platform that combines:

- **Sherlock** (patched v0.16.0) — username enumeration across 400+ platforms
- **GitNexus** — code intelligence engine used for reverse engineering and UI inspiration
- **线索网 Visualization** — interactive HTML spider-web investigation board

### Workflow

```
Username Input
     ↓
Variation Engine (up to 8 variants)
     ↓
Sherlock (patched) × each variant
     ↓
Deduplication + Category Grouping
     ↓
线索网 HTML Investigation Board
```

### System Requirements

- Python 3.10+
- pip (for dependency installation)
- Modern web browser (Chrome, Firefox, Edge recommended)
- Network connection (for platform checks)

---

*See individual wiki pages for detailed documentation.*
