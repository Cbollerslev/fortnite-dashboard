from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import httpx
import asyncio
import os

app = FastAPI()

API_KEY = os.environ.get("TRACKER_API_KEY", "")
BASE_URL = "https://public-api.tracker.gg/v2/fortnite/standard/profile/epic"

PLAYERS = [
    {"name": "FelixFuryOtto", "label": "Felix"},
    {"name": "ottawa-4700",   "label": "Ottawa"},
]

HEADERS = {
    "TRN-Api-Key": API_KEY,
    "Accept": "application/json",
}

async def fetch_player(client: httpx.AsyncClient, epic_name: str):
    try:
        r = await client.get(f"{BASE_URL}/{epic_name}", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def safe(d, *keys, default=0):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, {})
    return d if d is not None else default

def extract_stats(data, label, epic_name):
    if not data:
        return {"label": label, "name": epic_name, "error": True}

    segments = data.get("data", {}).get("segments", [])
    overall_seg = next((s for s in segments if s.get("type") == "overview"), None)
    if not overall_seg:
        return {"label": label, "name": epic_name, "error": True}

    stats = overall_seg.get("stats", {})

    def val(key):
        return safe(stats, key, "value", default=0) or 0

    def mode_seg(mode_key):
        return next((s for s in segments if s.get("type") == "playlist" and s.get("metadata", {}).get("key", "").lower() == mode_key), None)

    def mode_stats(seg):
        if not seg:
            return {"matches": 0, "wins": 0, "winPct": 0.0, "kills": 0, "kd": 0.0}
        s = seg.get("stats", {})
        def v(k): return safe(s, k, "value", default=0) or 0
        return {
            "matches": int(v("matches")),
            "wins":    int(v("wins")),
            "winPct":  round(v("winRate"), 1),
            "kills":   int(v("kills")),
            "kd":      round(v("kd"), 2),
        }

    return {
        "label": label,
        "name":  data.get("data", {}).get("platformInfo", {}).get("platformUserHandle", epic_name),
        "error": False,
        "overall": {
            "matches":       int(val("matches")),
            "wins":          int(val("wins")),
            "winPct":        round(val("winRate"), 1),
            "kills":         int(val("kills")),
            "kd":            round(val("kd"), 2),
            "top10":         int(val("top10")),
            "top25":         int(val("top25")),
            "minutesPlayed": int(val("minutesPlayed")),
        },
        "modes": {
            "solo":   mode_stats(mode_seg("p2")),
            "duos":   mode_stats(mode_seg("p10")),
            "squads": mode_stats(mode_seg("p9")),
        }
    }

@app.get("/api/stats")
async def get_stats():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[fetch_player(client, p["name"]) for p in PLAYERS])

    return [
        extract_stats(data, PLAYERS[i]["label"], PLAYERS[i]["name"])
        for i, data in enumerate(results)
    ]

app.mount("/", StaticFiles(directory="static", html=True), name="static")
