# Frequently Asked Questions

---

## General

### What is 线索网 (Clue Web)?
线索网 (pronounced "xiàn suǒ wǎng", meaning "Clue Web") is an OSINT investigation platform that combines Sherlock's username enumeration with a GitNexus-inspired interactive visualization. It finds all platforms where a username exists and displays the results as an interactive node graph.

### Is this the official Sherlock?
No. This is a **fork** of [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock) with 9 bug fixes and the added 线索网 investigation visualization layer. The original Sherlock project is maintained by its own team.

### What does OSINT mean?
**Open Source Intelligence** — gathering information from publicly available sources. In this context, checking if a username exists on public platforms.

### Is this legal?
Checking public profile pages is generally legal. However:
- Always respect platform Terms of Service
- Do not use this for harassment or stalking
- Be aware of your local laws regarding data collection
- Use responsibly and ethically

---

## Technical

### Why does my search find fewer results than expected?
- **Timeout too low**: Try `--timeout 20` for slower platforms
- **Network issues**: Some platforms may be temporarily down
- **Rate limiting**: Running too many searches quickly may trigger rate limits
- **Regional blocks**: Some platforms are region-specific

### Why do different variations find different numbers?
Each platform has its own username rules. Some allow dots (`john.doe`), some don't. Some are case-sensitive (`JohnDoe` ≠ `johndoe`). The variation engine exploits these differences.

### The HTML file is large / slow to open
Large investigations (300+ platforms) generate detailed HTML files. This is expected:
- The file is self-contained (no external dependencies)
- All data is embedded as JavaScript
- Canvas rendering handles ~500 nodes smoothly in modern browsers

### Can I search for multiple usernames at once?
Currently, `investigate.py` handles one target at a time. For multiple targets, run separate instances:
```bash
python investigate.py target1
python investigate.py target2
```

### How does the category detection work?
Platform URLs are matched against regex patterns for each category. For example:
- URL contains `tiktok`, `instagram`, `twitter` → **Social**
- URL contains `steam`, `xbox`, `playstation` → **Gaming**
- URL contains `github`, `stackoverflow` → **Tech**

Platforms that don't match any pattern go to **Other**.

---

## Bug Fixes

### Were these bugs reported upstream?
The bugs were found during this project and documented here. Users are encouraged to report them to the official Sherlock project.

### Bug 1 found 29 extra platforms — is that accurate?
Yes. Sites with `errorType` as a list (like `["status_code", "message"]`) were falling through to a less accurate detection path. After the fix, they use the correct detection method, revealing 29 additional valid profiles.

### Do the bug fixes break backward compatibility?
No. All fixes are internal improvements. The command-line interface, output format, and `data.json` schema remain unchanged.

---

## Visualization

### Can I save or share the investigation?
The generated HTML file is fully self-contained. You can:
- Send the HTML file as an email attachment
- Host it on any web server
- Open it offline in any browser
- Copy/paste the file to share

### Does the visualization need internet?
No. The HTML file works completely offline. All data, CSS, and JavaScript are embedded in the single file. The only internet action is when you click a SITE node to open a profile URL.

### Can I customize the colors?
Currently, category colors are defined in `CAT_META` within `investigate.py`. You can modify them before running an investigation:
```python
CAT_META = {
    'Social':   {'color': '#e91e63'},  # Change these hex colors
    'Gaming':   {'color': '#9c27b0'},
    ...
}
```

### Why does the minimap look different from the main canvas?
The minimap uses simplified rendering (smaller dots, thinner lines) for performance. It shows the same data but at a reduced detail level.

---

## Comparison

### How is this different from regular Sherlock?
| Feature | Sherlock (original) | 线索网 (this fork) |
|---------|--------------------|--------------------|
| Bug fixes | — | 9 bugs fixed (2 critical) |
| Variations | Manual (one username at a time) | Automatic (up to 8 variations) |
| Output | Terminal text | Interactive HTML investigation board |
| Visualization | None | Full spider-web graph with GitNexus-style features |
| Category analysis | None | 8 categories with color coding |
| Cross-referencing | None | Track which variation found each platform |

### How is this different from Maigret?
Maigret is a more comprehensive OSINT tool that checks 3,000+ sites and provides deeper analysis. 线索网 focuses on **visualization** — making investigation results explorable and interactive rather than just a text dump. They can be used together:
1. Run 线索网 for visual overview
2. Export URLs and feed into Maigret for deeper analysis
