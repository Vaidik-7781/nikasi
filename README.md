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
| `src/nikasi/agents/` | Sentinel, Verifier, Alerter (guarded model wording), Dispatcher (human approval) |
| `src/nikasi/telegram_bot.py`, `sender.py` | Telegram webhook and SQS alert sender |
| `web/` | offline-capable map app |
| `scripts/build_spots.py`, `deploy.sh`, `backtest.py` | spot building, one-command deploy, replay |
| `infra/template.yaml` | SAM: EventBridge, Lambda, DynamoDB, API Gateway, SQS+DLQ, S3+CloudFront |
| `docs/` | DEPLOY, WRITEUP, VIDEO_SCRIPT, SOLO_PLAN |
| `data/spots.seed.json` | seed spots, coordinates approximate |

## Run
`pip install pytest && pytest`, then `bash scripts/deploy.sh` (see `docs/DEPLOY.md`).

## Status (honest)
| Piece | State |
|---|---|
| Risk engine, templates, agent graph, API, Telegram bot, sender, web app | written, 36+ unit tests pass, not yet run on real AWS |
| Real data scripts (OSM, DEM), backtest | written, never run against live data |
| Deployed on AWS | not yet; see `docs/DEPLOY.md` |
| Spots | 3 seed spots with approximate coordinates |

## Status (details)
Thresholds in `risk.py` are placeholders until the backtest is run. Nothing here is validated yet.

Data: Open-Meteo (CC BY 4.0), Copernicus DEM GLO-30, OpenStreetMap contributors (ODbL).
