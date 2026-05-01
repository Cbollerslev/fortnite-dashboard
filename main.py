from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import asyncio
from typing import Optional

app = FastAPI()

FORTNITE_API = "https://fortnite-api.com/v2/stats/br/v2"

PLAYERS = [
    {"name": "FelixFuryOtto", "label": "Felix"},
    {"name": "ottawa-4700",   "label": "Ottawa"},
]

async def fetch_player(client: httpx.AsyncClient, epic_name: str):
    try:
        r = await client.get(FORTNITE_API, params={"name": epic_name}, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def extract_stats(data: dict, label: str, epic_name: str) -> dict:
    if not data or data.get("status") != 200:
        return {"label": label, "name": epic_name, "error": True}

    d = data["data"]
    account = d.get("account", {})
    stats = d.get("stats", {})
    all_stats = stats.get("all", {}).get("overall", {})
    solo = stats.get("all", {}).get("solo", {})
    duos = stats.get("all", {}).get("duo", {})
    squads = stats.get("all", {}).get("squad", {})

    def pct(wins, matches):
        if not matches:
            return 0.0
        return round(wins / matches * 100, 1)

    def kd(kills, deaths):
        if not deaths:
            return round(kills, 2) if kills else 0.0
        return round(kills / deaths, 2)

    def safe(d, key):
        return d.get(key, 0) or 0

    overall_matches = safe(all_stats, "matches")
    overall_wins    = safe(all_stats, "wins")
    overall_kills   = safe(all_stats, "kills")
    overall_deaths  = overall_matches - overall_wins

    return {
        "label": label,
        "name": account.get("name", epic_name),
        "error": False,
        "overall": {
            "matches":  overall_matches,
            "wins":     overall_wins,
            "winPct":   pct(overall_wins, overall_matches),
            "kills":    overall_kills,
            "kd":       kd(overall_kills, overall_deaths),
            "top3":     safe(all_stats, "top3"),
            "top5":     safe(all_stats, "top5"),
            "top6":     safe(all_stats, "top6"),
            "top10":    safe(all_stats, "top10"),
            "top12":    safe(all_stats, "top12"),
            "top25":    safe(all_stats, "top25"),
            "minutesPlayed": safe(all_stats, "minutesPlayed"),
        },
        "modes": {
            "solo":   _mode(solo),
            "duos":   _mode(duos),
            "squads": _mode(squads),
        }
    }

def _mode(m: dict) -> dict:
    matches = m.get("matches", 0) or 0
    wins    = m.get("wins", 0) or 0
    kills   = m.get("kills", 0) or 0
    deaths  = matches - wins
    return {
        "matches": matches,
        "wins":    wins,
        "winPct":  round(wins / matches * 100, 1) if matches else 0.0,
        "kills":   kills,
        "kd":      round(kills / deaths, 2) if deaths > 0 else (round(kills, 2) if kills else 0.0),
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
