# ============================================================
# ICYARR BACKEND — main.py
# ============================================================
# This FastAPI backend manages radio streams, loads M3U playlists,
# merges metadata, tests streams, and exposes endpoints for Tickarr
# and Dispatcharr integration.
# ============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# In-memory list of channel objects
# Each channel contains:
#   name, group, tvg_id, tvg_name, url, icy_title, bitrate, etc.
local_streams = []


# ============================================================
# DATA MODELS
# ============================================================

class M3URequest(BaseModel):
    url: str  # URL of the M3U file to load

class StreamRequest(BaseModel):
    url: str  # URL of the stream to test

class UpdateChannel(BaseModel):
    url: str
    name: str | None = None
    group: str | None = None


# ============================================================
# METADATA MERGE LOGIC
# ============================================================
# icyarr always keeps its own metadata if present.
# Incoming metadata only fills missing fields.

def merge_metadata(existing, incoming):
    merged = existing.copy()

    for key, value in incoming.items():
        if key not in merged or merged[key] in ("", None):
            merged[key] = value

    return merged


# ============================================================
# ADD CHANNEL OBJECT (WITH MERGE)
# ============================================================

def add_channel_object(channel):
    for existing in local_streams:
        if existing["url"] == channel["url"]:
            merged = merge_metadata(existing, channel)
            existing.update(merged)
            return

    local_streams.append(channel)


# ============================================================
# M3U LOADER ENDPOINT
# ============================================================

@app.post("/load_m3u")
def load_m3u(req: M3URequest):
    text = requests.get(req.url).text
    lines = text.splitlines()
    current = {}

    for line in lines:
        line = line.strip()

        if line.startswith("#EXTINF"):
            meta, name = line.split(",", 1)
            current["name"] = name

            parts = meta.split(" ")
            for part in parts:
                if "tvg-id" in part:
                    current["tvg_id"] = part.split("=")[1].strip('"')
                if "tvg-name" in part:
                    current["tvg_name"] = part.split("=")[1].strip('"')
                if "group-title" in part:
                    current["group"] = part.split("=")[1].strip('"')

        elif line and not line.startswith("#"):
            current["url"] = line
            add_channel_object(current)
            current = {}

    return local_streams


# ============================================================
# STREAM TESTER ENDPOINT
# ============================================================

@app.post("/test_stream")
def test_stream(req: StreamRequest):
    try:
        r = requests.get(req.url, timeout=5, stream=True)
        content_type = r.headers.get("Content-Type", "")

        if "audio" in content_type.lower():
            add_channel_object({"url": req.url})
            return {"status": "added", "url": req.url}

        return {"status": "invalid_stream", "content_type": content_type}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ============================================================
# LOCAL STREAM LIST ENDPOINT
# ============================================================

@app.get("/local_streams")
def get_local_streams():
    return local_streams


# ============================================================
# UPDATE CHANNEL ENDPOINT
# ============================================================

@app.patch("/update_channel")
def update_channel(req: UpdateChannel):
    for ch in local_streams:
        if ch["url"] == req.url:
            if req.name is not None:
                ch["name"] = req.name
            if req.group is not None:
                ch["group"] = req.group
            return {"status": "updated", "channel": ch}

    return {"status": "not_found", "url": req.url}


# ============================================================
# DELETE CHANNEL ENDPOINT
# ============================================================

@app.delete("/delete_channel")
def delete_channel(url: str):
    for ch in local_streams:
        if ch["url"] == url:
            local_streams.remove(ch)
            return {"status": "deleted", "url": url}

    return {"status": "not_found", "url": url}


# ============================================================
# TICKARR TEXT BUILDER
# ============================================================
# Builds a single "Now Playing" text string for Tickarr overlays.

def build_tickarr_text(channel: dict) -> str:
    parts = []

    icy_title = channel.get("icy_title") or channel.get("stream_title")
    name = channel.get("name") or channel.get("tvg_name")
    group = channel.get("group")
    bitrate = channel.get("bitrate")

    if icy_title:
        parts.append(icy_title)
    if name:
        parts.append(name)
    if group:
        parts.append(group)
    if bitrate:
        parts.append(f"{bitrate}kbps")

    if not parts:
        return "Unknown Station — No metadata available"

    return " — ".join(parts)


# ============================================================
# TICKARR TEXT ENDPOINT
# ============================================================
# Tickarr plugin calls this to get overlay text.

@app.get("/tickarr_text")
def tickarr_text(url: str):
    for ch in local_streams:
        if ch.get("url") == url:
            return {"text": build_tickarr_text(ch)}

    raise HTTPException(status_code=404, detail="Channel not found")


# ============================================================
# EXPORT M3U FOR DISPATCHARR ORGANIZER
# ============================================================
# Dispatcharr can import this URL directly.

@app.get("/export_m3u")
def export_m3u():
    lines = ["#EXTM3U"]

    for ch in local_streams:
        name = ch.get("name", "Unknown")
        group = ch.get("group", "")
        url = ch.get("url")

        extinf = f'#EXTINF:-1 group-title="{group}",{name}'
        lines.append(extinf)
        lines.append(url)

    return "\n".join(lines)
