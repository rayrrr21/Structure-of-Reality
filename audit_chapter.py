#!/usr/bin/env python3
"""
audit_chapter.py — Automated Forensic Linter & Style Scrubber for The Render Engine
Scans markdown draft files to prevent stylistic drift, AI clichés, filter words, 
and violations of the JIT Universe Narrative Bible.
"""

import sys
import re
import math
from pathlib import Path

# Banned idioms and stock AI clichés
BANNED_CLICHES = [
    r"breath (she|he|they) didn'?t know (she|he|they) (was|were) holding",
    r"shiver (ran|went) down (her|his|their) spine",
    r"blood ran cold",
    r"eyes widened in (shock|horror|surprise)",
    r"eyes flashed with a mix of",
    r"time seemed to slow down",
    r"predatory smile",
    r"mirthless smile",
    r"for what felt like an eternity",
    r"little did (he|she|they) know",
    r"as you know,?",
    r"couldn'?t help but (think|feel|wonder)",
    r"a testament to",
    r"tapestry of",
    r"dance of (shadows|light|death)",
]

# Filter words that distance the reader from sensory reality
FILTER_WORDS = [
    r"\b(she|he|they|I) (saw|watched|noticed|heard|felt|observed|realized|sensed)\b",
    r"\b(she|he|they|I) could (see|hear|feel|smell|taste)\b",
]

# Stated emotion labels (telling instead of showing through behavior)
STATED_EMOTIONS = [
    r"\bfear gripped\b",
    r"\bguilt washed over\b",
    r"\banger flared\b",
    r"\bpanic set in\b",
    r"\bsadness overwhelmed\b",
    r"\bnervously\b",
    r"\bangrily\b",
    r"\bfearfully\b",
    r"\bdesperately\b",
]

# Prohibited Physics Violations (Drift against JIT Bible)
PHYSICS_VIOLATIONS = [
    (r"\btravel(ed|ing)? back in time\b", "Violation: Backward time travel is impossible under JIT. Only forward uncollapsed branches can be observed."),
    (r"\bpsychic (power|ability|link)\b", "Violation: No magical or psychic powers. Nadir suspends quantum basis lock."),
    (r"\bglobal (collapse|reality crash)\b", "Violation: Glitches are strictly local to ~250m Causal Diamond, not planetary/global."),
    (r"\bdestroys the whole world\b", "Violation: Locality of Causal Diamond must be respected."),
]

def analyze_prose(text):
    print("=" * 70)
    print("🔍 RUNNING FORENSIC CRAFT & JIT CANON AUDIT")
    print("=" * 70)
    
    issues_found = 0
    
    # 1. Check Physics Violations
    print("\n[1/5] Checking JIT Universe Inviolable Canon...")
    for pattern, warning in PHYSICS_VIOLATIONS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            print(f"  ❌ CANON ERROR: {warning} (Found: '{m.group(0)}')")
            issues_found += 1
            
    # 2. Check Banned Clichés
    print("\n[2/5] Scanning for Banned Clichés & AI Stock Phrases...")
    for pattern in BANNED_CLICHES:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            print(f"  ❌ CLICHÉ DETECTED: '{m.group(0)}'")
            issues_found += 1
            
    # 3. Check Filter Words
    print("\n[3/5] Scanning for Filter Words (Sensory Distance)...")
    for pattern in FILTER_WORDS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            print(f"  ⚠️ FILTER WORD DETECTED: '{m.group(0)}' (Convert to unfiltered action)")
            issues_found += 1

    # 4. Check Stated Emotion Labels
    print("\n[4/5] Scanning for Stated Emotion Labels...")
    for pattern in STATED_EMOTIONS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            print(f"  ⚠️ EMOTIONAL EXPOSITION: '{m.group(0)}' (Show physical behavior instead)")
            issues_found += 1

    # 5. Sentence Cadence & Symmetry Metrics
    print("\n[5/5] Analyzing Prose Cadence & Sentence Asymmetry...")
    sentences = re.split(r'[.!?]+', text)
    word_counts = [len(s.split()) for s in sentences if len(s.split()) > 0]
    
    if word_counts:
        avg_len = sum(word_counts) / len(word_counts)
        variance = sum((x - avg_len) ** 2 for x in word_counts) / len(word_counts)
        std_dev = math.sqrt(variance)
        
        print(f"  • Total Sentences: {len(word_counts)}")
        print(f"  • Average Sentence Length: {avg_len:.1f} words")
        print(f"  • Sentence Length Standard Deviation: {std_dev:.1f} words")
        
        if std_dev < 4.0:
            print("  ⚠️ WARNING: Low cadence variance (prose may feel overly uniform/synthetic).")
            issues_found += 1
        else:
            print("  ✅ Cadence Variance: Healthy rhythmic asymmetry.")
            
    print("\n" + "=" * 70)
    if issues_found == 0:
        print("🎉 AUDIT PASSED: Prose satisfies top-tier NYC Bestseller & JIT standards.")
    else:
        print(f"⚠️ AUDIT COMPLETE: {issues_found} potential issue(s) identified for scrub pass.")
    print("=" * 70)
    return issues_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit_chapter.py <path_to_chapter_markdown>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
        
    content = file_path.read_text(encoding='utf-8')
    analyze_prose(content)
