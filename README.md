# Nikasi

Go / caution / no-go for named underpasses during monsoon rain, Delhi first.
Built during WeMakeDevs x AWS Environmental Hacks (Oct 8-11, 2026), Heat and Water track.

**Principle:** terrain and rain decide safety; agents explain it and never override it.
Stale or missing data shows as UNKNOWN and is treated as NO-GO.

## Layout
| Path | What |
|---|---|
| `src/nikasi/risk.py` | deterministic risk engine (no model, no network) |
| `src/nikasi/weather.py` | Open-Meteo fetch, fails to None |
| `src/nikasi/handler.py` | Lambda, every 15 min, writes state to DynamoDB |
| `scripts/dem_pockets.py` | low-pocket depth from Copernicus DEM (untested scaffold) |
| `scripts/osm_underpasses.py` | underpass list from OSM (untested scaffold) |
| `infra/template.yaml` | SAM: EventBridge -> Lambda -> DynamoDB (TTL) |
| `data/spots.seed.json` | seed spots, coordinates approximate |

## Run
`pip install pytest && pytest` - then `sam build && sam deploy --guided --region ap-south-1`.

## Status
Thresholds in `risk.py` are placeholders until the backtest is run. Nothing here is validated yet.

Data: Open-Meteo (CC BY 4.0), Copernicus DEM GLO-30, OpenStreetMap contributors (ODbL).
