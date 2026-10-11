# Nikasi

**Go, caution or no-go for named Delhi underpasses during monsoon rain, with a countdown to no-go.**
Built solo by Vaidik Gupta (team SocialStar) for WeMakeDevs x AWS Environmental Hacks, Oct 8-11 2026, Heat and Water track.

> Terrain and rain decide safety. Agents explain it and never override it. Missing or old data shows UNKNOWN and is treated as NO-GO.

## See it in 60 seconds (no AWS, no installs beyond Python 3.11+)
```
python scripts/local_demo.py          # open http://localhost:8000
PYTHONPATH=src python -m nikasi.replay   # same storm as a text timeline
pip install pytest && pytest             # 46 tests
```
The demo plays a **synthetic** storm through the real code path, one 15-minute step every 5 seconds: GO, then CAUTION with a countdown, then NO-GO, then a weather outage that flips every card to UNKNOWN, then recovery. A scripted stand-in model tries to say "definitely safe" and the Alerter throws it away. It is a behaviour demo, not real rain and not an accuracy claim.

## How it decides
| Piece | What it does | File |
|---|---|---|
| Risk engine | Rain now, next 2 h, past 24 h, low-pocket depth, known flood spot -> state + minutes to no-go. No model, no network. | `src/nikasi/risk.py` |
| Sentinel | Detects state changes | `src/nikasi/agents/sentinel.py` |
| Verifier | Worse is accepted at once; better must hold one more reading | `src/nikasi/agents/verifier.py` |
| Alerter | Fixed templates; a model may reword, but is dropped if it adds numbers, claims safety, or drops the verdict | `src/nikasi/agents/alerter.py` |
| Dispatcher | Proposes a barricade list; needs a named, signed-in approver | `src/nikasi/agents/dispatcher.py`, `src/nikasi/ops.py` |
| Telegram bot | Alerts for the 3 nearest spots; stores a chat id for 24 h; `/stop` erases | `src/nikasi/telegram_bot.py`, `sender.py` |
| Web app | Cards + optional map, offline shell, re-checks data age in the browser | `web/` |

Every failure mode and the test that covers it: [`docs/SAFETY_CASE.md`](docs/SAFETY_CASE.md). Diagram: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## AWS design
EventBridge (15 min) -> Lambda -> DynamoDB (TTL); API Gateway + Lambda read API; SQS + dead-letter queue -> Lambda -> Telegram; S3 + CloudFront (private bucket, OAC); Cognito JWT for the ward console; CloudWatch alarms -> SNS; optional Amazon Bedrock with Guardrails (or Strands Agents) for alert wording. All in one SAM template, `infra/template.yaml`.

## Honest status
| Piece | State |
|---|---|
| Risk engine, agents, API, bot, sender, ward console API, web app | written, 46 unit tests pass in CI |
| `infra/template.yaml` | passes `cfn-lint`; **not deployed to AWS** (see `docs/DEPLOY.md` to deploy) |
| Thresholds | placeholders, **not calibrated**; the backtest needs real flood reports in `data/flood_events.json` and has not been run |
| OSM and DEM scripts | written, never run on live data; `src/nikasi/spots.json` holds 3 seed spots with approximate coordinates |
| Bedrock / Strands wording | code present, not run against a live model |

## Data and privacy
Open-Meteo (CC BY 4.0), Copernicus DEM GLO-30, OpenStreetMap contributors (ODbL). Privacy-by-design in the spirit of India's DPDP Act 2023: no accounts for the public, location never stored. Design intent, not legal advice. Guidance, not a guarantee: if there is water on the road, do not enter.

License: MIT.
