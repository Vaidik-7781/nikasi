# Solo build plan (one builder: Vaidik)

All work is done by one person. No lanes, no handoffs. Order is by value to the judges, and every step ends in something that runs.

Data contract (DynamoDB item): `{spot_id, name, state, act_as, reasons[], minutes_to_no_go, updated_at, ttl}`

| # | Step | Files | Done when | Time |
|---|---|---|---|---|
| 1 | Deploy core to AWS | `infra/template.yaml` | `/spots` returns live states; DynamoDB rows appear | Fri |
| 2 | Real spots | `scripts/osm_underpasses.py`, `data/spots.seed.json` | 10-15 Delhi spots snapped to OSM ways | Fri |
| 3 | DEM pockets | `scripts/dem_pockets.py` | `pocket_depth_m` filled, eyeballed against known sites | Fri night |
| 4 | Backtest | `scripts/backtest.py`, `data/flood_events.json` | one real day, precision/recall/lead time, honest | Sat AM |
| 5 | Web map | `web/` | map + cards + countdown reading `/spots` | Sat |
| 6 | Telegram bot | `src/nikasi/telegram_bot.py`, `sender.py` | alert reaches phone; `/stop` erases | Sat PM |
| 7 | Agents (Strands + Bedrock Guardrails) | `src/nikasi/agents/` | explains alert; model off = template still sends | Sat night |
| 8 | Freeze, video, writeup, blog | `docs/` | video <3 min shows AWS console; submit Sun | Sun |

Cut order if short on time: agents polish, offline mode, route check, second city. Never cut: step 1, 4, and UNKNOWN = NO-GO.
