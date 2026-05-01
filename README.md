# Fortnite Stats Dashboard

Dashboard der viser og sammenligner stats for to Fortnite-spillere.

## Spillere konfigureret
- FelixFuryOtto
- ottawa-4700

## Deploy til Railway

### Forudsætninger
- Railway CLI installeret: `npm install -g @railway/cli`
- Logget ind: `railway login`

### Trin

```bash
# 1. Opret nyt projekt på Railway
railway init

# 2. Deploy
railway up

# 3. Åbn i browser
railway open
```

### Skift spillere
Rediger `PLAYERS`-listen i `main.py`:

```python
PLAYERS = [
    {"name": "EpicGamesNavn1", "label": "Visningsnavn1"},
    {"name": "EpicGamesNavn2", "label": "Visningsnavn2"},
]
```

## Krav
- Spillernes stats skal være **offentlige** på Epic Games / fortnite-api.com
- Brug det præcise Epic Games brugernavn (case-sensitive)

## Lokalt
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Åbn http://localhost:8000
```
