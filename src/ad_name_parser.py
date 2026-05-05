import re
from dataclasses import dataclass
from typing import Optional

# Regex to find creative IDs like BATCH#61, Bounty#27, UGC#15
_CREATIVE_ID_RE = re.compile(r"(BATCH|Bounty|UGC)#(\d+)", re.IGNORECASE)

# Segments that indicate iteration type
_ITERATION_TYPES = {"ITER", "IDEA", "RAW", "NET NEW", "Creator"}

# Segments that indicate media type
_MEDIA_TYPES = {"Video", "Statics"}

# Version pattern: V1, V2, V1.1, V2.3, etc.
_VERSION_RE = re.compile(r"^V\d+(?:\.\d+)?$")


@dataclass
class AdMetadata:
    creative_id: str  # "BATCH#61", "Bounty#27", "UGC#15", "Mashup"
    creative_type: str  # "BATCH", "BOUNTY", "UGC", "Mashup"
    creative_number: Optional[int]  # 61, 27, 15, None for Mashup
    iteration_source: Optional[str]  # "BATCH#45 Iteration", None
    landing_page: Optional[str]  # "E-LP: Comfort V1", "/url-path"
    media_type: Optional[str]  # "Video", "Statics"
    iteration_type: Optional[str]  # "ITER", "IDEA", "RAW", "NET NEW"
    creator: Optional[str]  # "Mufariz", "Kamariddin"
    version: Optional[str]  # "V2", "V3"
    copy_variants: Optional[str]  # "C#1, #4"
    headline_variants: Optional[str]  # "H#1, #2"
    raw_name: str  # Full original ad name


def extract_creative_id(ad_name: str) -> Optional[str]:
    """Extract the creative ID (e.g. 'BATCH#61') from an ad name.

    Returns None if no recognized creative ID is found.
    """
    match = _CREATIVE_ID_RE.search(ad_name)
    if match:
        # Normalize type to uppercase for BATCH/UGC, title case for Bounty
        return match.group(0)
    return None


def parse_ad_name(ad_name: str) -> AdMetadata:
    """Parse a Meta ad name string into structured metadata."""
    raw_name = ad_name

    # Detect format: pipe-delimited vs dash-delimited
    if " | " in ad_name and not _is_dash_delimited(ad_name):
        return _parse_pipe_style(ad_name, raw_name)
    else:
        return _parse_dash_style(ad_name, raw_name)


def _is_dash_delimited(ad_name: str) -> bool:
    """Determine if a pipe-containing name is actually dash-delimited.

    Some EAM-style names mention 'Mashup' in a description segment
    but are still dash-delimited (e.g. 'EAM BATCH#32 - Top Performing UGC Mashup - ...').
    """
    return ad_name.startswith("EAM ") or ad_name.startswith("BED EAM ") or ad_name.startswith("BATCH#")


def _parse_dash_style(ad_name: str, raw_name: str) -> AdMetadata:
    """Parse dash-delimited ad names (EAM-style, BED EAM, BATCH-only)."""
    # Strip trailing " - Copy" or " – Copy" (en-dash variant)
    cleaned = re.sub(r"\s*[-–]\s*Copy\s*$", "", ad_name)

    segments = [s.strip() for s in cleaned.split(" - ")]

    # Extract creative ID from the first segment (or anywhere)
    creative_id_str = extract_creative_id(cleaned)
    creative_type = None
    creative_number = None

    if creative_id_str:
        match = _CREATIVE_ID_RE.search(creative_id_str)
        if match:
            creative_type = match.group(1).upper()
            creative_number = int(match.group(2))
    else:
        creative_type = "Unknown"

    # Two-pass classification: first identify pattern-matched segments,
    # then assign creator as the unclassified segment immediately before version.
    iteration_source = None
    landing_page = None
    media_type = None
    iteration_type = None
    creator = None
    version = None
    copy_variants = None
    headline_variants = None

    # Track which indices are classified and where version is
    work_segments = segments[1:]  # skip first (creative ID / brand prefix)
    classified = set()
    version_idx = None

    # Pass 1: classify segments with clear content patterns
    for i, seg in enumerate(work_segments):
        seg_stripped = seg.strip()
        if not seg_stripped:
            classified.add(i)
            continue

        if "Iteration" in seg_stripped and _CREATIVE_ID_RE.search(seg_stripped):
            iteration_source = seg_stripped
            classified.add(i)
        elif seg_stripped.startswith(("LP:", "E-LP:", "LP :")):
            landing_page = seg_stripped
            classified.add(i)
        elif seg_stripped.startswith("/"):
            landing_page = seg_stripped
            classified.add(i)
        elif seg_stripped.startswith("C#"):
            copy_variants = seg_stripped
            classified.add(i)
        elif seg_stripped.startswith("H#"):
            headline_variants = seg_stripped
            classified.add(i)
        elif _VERSION_RE.match(seg_stripped):
            version = seg_stripped
            version_idx = i
            classified.add(i)
        elif seg_stripped in _MEDIA_TYPES:
            media_type = seg_stripped
            classified.add(i)
        elif seg_stripped.upper() in {it.upper() for it in _ITERATION_TYPES}:
            iteration_type = seg_stripped.upper() if seg_stripped.upper() != "CREATOR" else "Creator"
            classified.add(i)

    # Pass 2: assign creator as the nearest unclassified segment before version
    if version_idx is not None:
        for candidate_idx in range(version_idx - 1, -1, -1):
            if candidate_idx not in classified:
                creator = work_segments[candidate_idx].strip()
                classified.add(candidate_idx)
                break

    return AdMetadata(
        creative_id=creative_id_str or "Unknown",
        creative_type=creative_type or "Unknown",
        creative_number=creative_number,
        iteration_source=iteration_source,
        landing_page=landing_page,
        media_type=media_type,
        iteration_type=iteration_type,
        creator=creator,
        version=version,
        copy_variants=copy_variants,
        headline_variants=headline_variants,
        raw_name=raw_name,
    )


def _parse_pipe_style(ad_name: str, raw_name: str) -> AdMetadata:
    """Parse pipe-delimited ad names (Mashup and other | styles)."""
    segments = [s.strip() for s in ad_name.split(" | ")]

    # Try to find a creative ID in the full name
    creative_id_str = extract_creative_id(ad_name)
    creative_type = None
    creative_number = None

    if creative_id_str:
        match = _CREATIVE_ID_RE.search(creative_id_str)
        if match:
            creative_type = match.group(1).upper()
            creative_number = int(match.group(2))
    elif "Mashup" in ad_name:
        creative_id_str = "Mashup"
        creative_type = "Mashup"
    else:
        creative_id_str = "Unknown"
        creative_type = "Unknown"

    # Extract what we can from pipe segments
    media_type = None
    landing_page = None
    iteration_type = None

    for seg in segments:
        if seg in _MEDIA_TYPES:
            media_type = seg
        elif seg.startswith(("LP:", "E-LP:", "/", "pages/")):
            landing_page = seg
        elif seg.upper() in {it.upper() for it in _ITERATION_TYPES}:
            iteration_type = seg.title() if seg.upper() == "NET NEW" else seg.upper()

    return AdMetadata(
        creative_id=creative_id_str,
        creative_type=creative_type or "Unknown",
        creative_number=creative_number,
        iteration_source=None,
        landing_page=landing_page,
        media_type=media_type,
        iteration_type=iteration_type,
        creator=None,
        version=None,
        copy_variants=None,
        headline_variants=None,
        raw_name=raw_name,
    )
