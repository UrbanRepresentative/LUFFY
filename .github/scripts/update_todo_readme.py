#!/usr/bin/env python3
"""One-shot deterministic sync of README 'Complete TODO List'.
Only the TODO changes introduced by the main->dev code changes are applied;
all other README bullets are preserved byte-for-byte.
"""
import re
import pathlib

README = pathlib.Path("README.md")

FINAL = [
    ("luffy/deepscaler/utils.py", 45, "Add logging for API calls and errors"),
    ("luffy/deepscaler/utils.py", 46, "Support batch processing for multiple prompts"),
    ("luffy/deepscaler/utils.py", 47, "Add timeout configuration for API calls"),
    ("luffy/deepscaler/utils.py", 107, "Implement Vertex AI initialization and authentication"),
    ("luffy/deepscaler/utils.py", 108, "Configure safety settings for content generation"),
    ("luffy/deepscaler/utils.py", 109, "Set up GenerativeModel with proper system instructions"),
    ("luffy/deepscaler/utils.py", 110, "Implement retry logic with exponential backoff"),
    ("luffy/deepscaler/utils.py", 111, "Add comprehensive error handling for API access issues"),
    ("luffy/deepscaler/utils.py", 112, "Handle rate limiting and quota management"),
    ("luffy/deepscaler/utils.py", 113, "Implement response validation and text extraction"),
    ("luffy/deepscaler/utils.py", 114, "Add support for different generation configurations"),
    ("luffy/verl/verl/protocol.py", 114, "Optimize memory usage during tensor reshaping"),
    ("luffy/verl/verl/protocol.py", 115, "Add support for different tensor types and shapes"),
    ("luffy/verl/verl/protocol.py", 136, "Optimize tensor view operations for performance"),
    ("luffy/verl/verl/protocol.py", 137, "Add error handling for invalid batch dimensions"),
    ("luffy/verl/verl/protocol.py", 169, "(zhangchi.usc1992) add consistency check"),
    ("luffy/verl/verl/protocol.py", 265, "we can actually lift this restriction if needed"),
    ("luffy/verl/verl/protocol.py", 351, "(zhangchi.usc1992) whether to copy"),
]

CHANGED = {"luffy/deepscaler/utils.py", "luffy/verl/verl/protocol.py"}

BULLET_RE = re.compile(r"^- \[ \] \*\*(?P<path>.+?):(?P<line>\d+)\*\* - (?P<msg>.*)$")
HEADER_RE = re.compile(r"^###[ \t]+📝[ \t]+Complete TODO List[ \t]*$", re.M)
NEXT_H_RE = re.compile(r"^##[ \t]+", re.M)

text = README.read_text(encoding="utf-8")
h = HEADER_RE.search(text)
assert h, "section header not found"
nxt = NEXT_H_RE.search(text, h.end())
assert nxt, "next heading not found"

head = text[:h.end()]
tail = text[nxt.start():]
segment = text[h.end():nxt.start()]

kept = []
removed = []
for raw in segment.splitlines():
    m = BULLET_RE.match(raw)
    if not m:
        continue
    item = (m.group("path"), int(m.group("line")), m.group("msg"))
    (removed if item[0] in CHANGED else kept).append(item)

kept.extend(FINAL)
kept.sort(key=lambda x: (x[0], x[1]))

bullets = [f"- [ ] **{p}:{ln}** - {msg}" for p, ln, msg in kept]
README.write_text(head + "\n" + "\n".join(bullets) + "\n\n" + tail, encoding="utf-8")

print("removed old bullets for changed files:", len(removed))
print("total TODO bullets after sync:", len(kept))
print("---- final entries for changed files (path:line - message) ----")
for p, ln, msg in kept:
    if p in CHANGED:
        print(f"{p}:{ln} - {msg}")

last_by_path = {}
for p, ln, _ in kept:
    assert ln > last_by_path.get(p, -1), (p, ln)
    last_by_path[p] = ln
print("ordering check passed: path lexicographic, lines ascending within each file")
print("changed-file bullet count:", sum(1 for p, _, _ in kept if p in CHANGED))
