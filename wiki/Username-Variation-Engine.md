# Username Variation Engine

The variation engine automatically generates alternate forms of the target username to maximize discovery across platforms where users may register with slightly different name formats.

---

## How It Works

Given an input username, the engine applies a set of **deterministic transformations** to produce up to 8 variations (configurable via `--max-variations`).

### Transformation Rules

| # | Rule | Input | Output |
|---|------|-------|--------|
| 1 | Original | `sleepy_lemonade` | `sleepy_lemonade` |
| 2 | Remove separators | `sleepy_lemonade` | `sleepylemonade` |
| 3 | Underscore → dot | `sleepy_lemonade` | `sleepy.lemonade` |
| 4 | Underscore → hyphen | `sleepy_lemonade` | `sleepy-lemonade` |
| 5 | camelCase | `sleepy_lemonade` | `sleepyLemonade` |
| 6 | PascalCase | `sleepy_lemonade` | `SleepyLemonade` |
| 7 | Reversed parts | `sleepy_lemonade` | `lemonade_sleepy` |
| 8 | Reversed (no sep) | `sleepy_lemonade` | `lemonadesleepy` |

### Separator Detection

The engine detects separators in this order:
1. Underscore `_`
2. Dot `.`
3. Hyphen `-`
4. Space ` `
5. CamelCase boundaries (e.g., `SleepyLemonade` → `Sleepy`, `Lemonade`)

If no separator is found, fewer variations are generated (only the original and case variants).

### Deduplication

Variations are deduplicated before being searched:
- `john.doe` with dot→underscore produces `john_doe` — if this equals the original, it's skipped
- Case-insensitive dedup: `JohnDoe` and `johndoe` are treated as different (platforms are case-sensitive)

### Limiting Variations

Use `--max-variations N` to cap the number:
```bash
python investigate.py sleepy_lemonade --max-variations 3
# Only searches: sleepy_lemonade, sleepylemonade, sleepy.lemonade
```

### Single-Word Usernames

For usernames without separators (e.g., `xXDarkLordXx`):
```
Input: xXDarkLordXx
Variations:
  - xXDarkLordXx (original)
  - xxdarklordxx (lowercase)
  - xXDarkLord_Xx (CamelCase split with underscore)
```

---

## Why Variations Matter

### Real-World Example

Searching `sleepy_lemonade` alone finds 89 platforms. But the same person might use:

| Variant | Extra Hits | Platforms |
|---------|-----------|-----------|
| `sleepylemonade` | +24 unique | GitHub, Steam, Reddit |
| `sleepy.lemonade` | +18 unique | Instagram, Spotify |
| `sleepy-lemonade` | +12 unique | Medium, Dev.to |
| `sleepyLemonade` | +8 unique | Discord, Twitch |

Total: 242 unique platforms vs. 89 with original only — **2.7× more coverage**.

### Cross-Referencing

The Clue Web visualization tracks **which variation** found each platform (the `sources` field). This enables:

1. **Source attribution**: See exactly which username format is used on each platform
2. **Overlap analysis**: Platforms found by multiple variants strongly suggest the same person
3. **Variant filtering**: Click a variant in the UI to see only its findings
4. **Pattern detection**: If `sleepy.lemonade` is used on professional platforms and `sleepylemonade` on gaming platforms, this reveals intentional separation

---

## Code Reference

The variation engine is in `investigate.py`, function `generate_variations()`:

```python
def generate_variations(username, max_count=8):
    """Generate username variations by swapping separators and casing."""
    # 1. Detect separator and split parts
    # 2. Apply transformation rules
    # 3. Deduplicate
    # 4. Return up to max_count variations
```

Each variation is then passed to `run_sherlock()` which calls Sherlock as a subprocess:

```python
def run_sherlock(username, timeout=10):
    """Run patched Sherlock for a single username variation."""
    # subprocess.run(['python', '-m', 'sherlock_project.sherlock', '--local', username])
    # Parse [+] lines from stdout
    # Return list of {site, url, username}
```
