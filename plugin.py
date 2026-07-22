import requests

# ============================================================
# ICYARR BASE URL
# ------------------------------------------------------------
# IMPORTANT:
# Replace "http://your-icyarr-host" with the actual URL where
# your Icyarr backend is reachable.
#
# Examples:
#   "http://localhost:8000"
#   "http://192.168.1.50:8000"
#   "https://icyarr.yourdomain.com"
# ============================================================
ICYARR_BASE = "http://your-icyarr-host"


# ============================================================
# FETCH NOW PLAYING TEXT FROM ICYARR
# ------------------------------------------------------------
# Calls Icyarr's /tickarr_text endpoint and returns the text
# string used for Tickarr overlays.
# ============================================================
def fetch_icyarr_text(stream_url: str) -> str:
    try:
        r = requests.get(
            f"{ICYARR_BASE}/tickarr_text",
            params={"url": stream_url},
            timeout=5
        )
        r.raise_for_status()

        data = r.json()
        return data.get("text", "Unknown Station — No metadata available")

    except Exception:
        # If Icyarr is unreachable or errors, fall back gracefully
        return "Unknown Station — No metadata available"


# ============================================================
# MAIN TICKARR PLUGIN ENTRY POINT
# ------------------------------------------------------------
# Tickarr automatically calls run(channel, state)
#
# channel: Tickarr channel object
# state:   persistent dict for this plugin/channel
#
# This function:
#   1. Checks if the channel is active
#   2. Gets the stream URL Tickarr is playing
#   3. Fetches Now Playing text from Icyarr
#   4. Compares with last applied text
#   5. Updates Tickarr overlay if changed
#   6. Saves new text in plugin state
# ============================================================
def run(channel, state):

    # ------------------------------------------------------------
    # 1. Only run when someone is watching the channel
    # ------------------------------------------------------------
    if not channel.is_active:
        return  # nobody watching → no overlay update needed

    # ------------------------------------------------------------
    # 2. Get the stream URL Tickarr is currently playing
    # ------------------------------------------------------------
    stream_url = channel.source_url

    # ------------------------------------------------------------
    # 3. Fetch Now Playing text from Icyarr
    # ------------------------------------------------------------
    new_text = fetch_icyarr_text(stream_url)

    # ------------------------------------------------------------
    # 4. Compare to last applied text
    # ------------------------------------------------------------
    last_text = state.get("last_text")

    if new_text == last_text:
        return  # no change → avoid unnecessary overlay updates

    # ------------------------------------------------------------
    # 5. Update Tickarr Custom Text overlay
    # ------------------------------------------------------------
    channel.custom_text = new_text
    channel.update_custom_text()   # Tickarr API call

    # ------------------------------------------------------------
    # 6. Save new text for next comparison
    # ------------------------------------------------------------
    state["last_text"] = new_text
