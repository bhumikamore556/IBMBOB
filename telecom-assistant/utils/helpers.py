"""
Utility helpers used across the application.
"""

import os
import re
from typing import List, Dict, Any
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Remove characters that are unsafe for filenames."""
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def format_file_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    return f"{size_bytes / (1024 ** 3):.1f} GB"


def ensure_dir(path: str) -> None:
    """Create directory if it does not exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Truncate text to max_chars and append ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def build_score_badge(percentage: float) -> str:
    """Return a colour label based on quiz score percentage."""
    if percentage >= 80:
        return "🟢 Excellent"
    elif percentage >= 60:
        return "🟡 Good"
    elif percentage >= 40:
        return "🟠 Needs Improvement"
    return "🔴 Keep Studying"


def get_learning_recommendations(incorrect_results: List[Dict[str, Any]]) -> str:
    """
    Generate a short study recommendation string based on incorrect answers.
    """
    if not incorrect_results:
        return "Great job! Review all topics to maintain your understanding."

    topics = [r["question"][:80] for r in incorrect_results[:5]]
    rec_lines = ["Based on your incorrect answers, we recommend reviewing:"]
    for t in topics:
        rec_lines.append(f"  • {t}")
    rec_lines.append(
        "\nTip: Upload relevant learning materials and use 'Ask Telecom Assistant' "
        "to get detailed explanations on these topics."
    )
    return "\n".join(rec_lines)


TELECOM_TOPICS = [
    "5G",
    "4G / LTE",
    "OFDM",
    "MIMO",
    "Beamforming",
    "Modulation",
    "Antenna & Propagation",
    "Base Station",
    "RAN (Radio Access Network)",
    "Core Network",
    "Network Slicing",
    "Handover",
    "Signal Processing",
    "IoT Communication",
    "Network Protocols",
    "Wireless Communication",
    "Spectrum Management",
    "Small Cells",
    "mmWave",
    "Channel Coding",
]
