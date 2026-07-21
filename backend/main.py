# Import FastAPI to create the backend API server
from fastapi import FastAPI

# Import BaseModel to define request body structures
from pydantic import BaseModel

# Import requests so we can fetch M3U files and test stream URLs
import requests


# Create the FastAPI application instance
app = FastAPI()

# This list will store all channel objects in memory
# Each object contains: name, group, tvg-id, tvg-name, url
local_streams = []


# ============================================================
# DATA MODELS
# ============================================================

class M3URequest(BaseModel):
    # The URL of the M3U file the user wants to load
    url: str

class StreamRequest(BaseModel):
    # The URL of the stream the user wants to test
    url: str

class UpdateChannel(BaseModel):
    # URL identifies the station uniquely
    url: str
    # Optional new name (None means "don't change")
    name: str | None = None
    # Optional new group (None means "don't change")
    group: str | None = None


# ============================================================
# METADATA MERGE LOGIC
# ============================================================

def merge_metadata(existing, incoming):
    # Make a copy of the existing channel so we don't mutate it directly
    merged = existing.copy()

    # Loop through each metadata field in the incoming channel
    for key, value in incoming.items():

        # If icyarr has no value for this field, accept the incoming value
        if key not in merged or merged[key] in ("", None):
            merged[key] = value

        # If icyarr already has a value, keep it (icyarr wins)
        else:
            continue

    # Return the merged channel object
    return merged


# ============================================================
# M3U LOADER ENDPOINT
# ============================================================

@app.post("/load_m3u")
def load_m3u(req: M3URequest):
    # Download the M3U file text from the provided URL
    text = requests.get(req.url).text

    # Split the file into individual lines
    lines = text.splitlines()

    # Temporary dictionary to hold metadata for each channel
    current = {}

    # Loop through each line in the M3U file
    for line in lines:
        line = line.strip()

        # If the line starts with #EXTINF, it contains metadata
        if line.startswith("#EXTINF"):

            # Split metadata from the channel name
            meta, name = line.split(",", 1)
            current["name"] = name

            # Split metadata attributes into parts
            parts = meta.split(" ")

            # Extract tvg-id, tvg-name, group-title if present
            for part in parts:
                if "tvg-id" in part:
                    current["tvg_id"] = part.split("=")[1].strip('"')
                if "tvg-name" in part:
                    current["tvg_name"] = part.split("=")[1].strip('"')
                if "group-title" in part:
                    current["group"] = part.split("=")[1].strip('"')

        # If the line is not metadata and not empty, it is the stream URL
        elif line and not line.startswith("#"):

            # Store the stream URL
            current["url"] = line

            # Add the channel to the local list (with merge logic)
            add_channel_object(current)

            # Reset for next channel
            current = {}

    # Return the full list of channels after loading
    return local_streams


# ============================================================
# ADD CHANNEL OBJECT (WITH MERGE)
# ============================================================

def add_channel_object(channel):
    # Loop through existing channels
    for existing in local_streams:

        # If URLs match, this is the same station → merge metadata
        if existing["url"] == channel["url"]:
            merged = merge_metadata(existing, channel)
            existing.update(merged)
            return

    # If no match found, this is a new station → add it
    local_streams.append(channel)


# ============================================================
# STREAM TESTER ENDPOINT
# ============================================================

@app.post("/test_stream")
def test_stream(req: StreamRequest):
    try:
        # Try to open the stream URL with a timeout
        r = requests.get(req.url, timeout=5, stream=True)

        # Get the content type from the response headers
        content_type = r.headers.get("Content-Type", "")

        # If the content type contains "audio", it's a valid stream
        if "audio" in content_type.lower():

            # Add the stream to the local list (minimal metadata)
            add_channel_object({"url": req.url})

            # Return success
            return {"status": "added", "url": req.url}

        # If not audio, return invalid stream info
        return {"status": "invalid_stream", "content_type": content_type}

    except Exception as e:
        # If any error occurs (timeout, connection error, etc.)
        return {"status": "error", "detail": str(e)}


# ============================================================
# LOCAL STREAM LIST ENDPOINT
# ============================================================

@app.get("/local_streams")
def get_local_streams():
    # Return the full list of channel objects
    return local_streams


# ============================================================
# UPDATE NAME/GROUP ENDPOINT
# ============================================================

@app.patch("/update_channel")
def update_channel(req: UpdateChannel):
    # Loop through channels
    for ch in local_streams:

        # Match by URL (unique identifier)
        if ch["url"] == req.url:

            # Update name if provided
            if req.name is not None:
                ch["name"] = req.name

            # Update group if provided
            if req.group is not None:
                ch["group"] = req.group

            # Return updated channel
            return {"status": "updated", "channel": ch}

    # If no channel matches the URL
    return {"status": "not_found", "url": req.url}

# ============================================================
# DELETE CHANNEL ENDPOINT
# ============================================================

@app.delete("/delete_channel")
def delete_channel(url: str):
    # Loop through all stored channels
    for ch in local_streams:

        # Check if this channel's URL matches the one we want to delete
        if ch["url"] == url:

            # Remove the channel object from the list
            local_streams.remove(ch)

            # Return confirmation that deletion succeeded
            return {"status": "deleted", "url": url}

    # If no channel matched the URL, return a not-found response
    return {"status": "not_found", "url": url}
