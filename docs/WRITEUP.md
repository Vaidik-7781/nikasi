# Nikasi: writeup (submission draft)

> Fill every [BRACKET] with a real result before submitting. Do not publish a number you did not measure.

## Problem
Every monsoon, Delhi underpasses such as Minto Bridge fill with water within minutes and people drive in. Existing rain alerts cover a whole city, not the one underpass on your route. Nikasi answers one question for a named underpass: go, caution or no-go, and how long until no-go.

## What it does
- Scores each underpass every 15 minutes from rain now, rain in the next two hours, rain in the last 24 hours, how low the spot sits, and whether it is a known flood spot.
- Shows GO / CAUTION / NO-GO with a countdown on a web map that keeps working offline, and sends Telegram alerts when a spot you are near changes.
- Fail-safe by design: old or missing data shows UNKNOWN and is treated as NO-GO, in the backend, the API and the browser.

## How it is built
| Part | AWS service / tool |
|---|---|
| 15-minute schedule | EventBridge -> Lambda risk engine |
| State | DynamoDB with TTL |
| Read API | API Gateway (HTTP) + Lambda |
| Web app | S3 + CloudFront (private bucket, origin access control) |
| Alerts | SQS with dead-letter queue -> Lambda sender -> Telegram; Secrets Manager for the bot token |
| Agent graph | Sentinel -> Verifier -> Alerter -> Dispatcher in Python; Amazon Bedrock with Guardrails can reword alerts |
| Infra as code | AWS SAM (`infra/template.yaml`) |

Agent design: a model is never on the safety path. The risk engine and the Verifier (an improvement must hold for two readings before a warning is lifted) are plain code with tests. The Alerter may ask a model to reword, but its text is used only if it keeps the verdict word, adds no number that is not in the fixed template, and claims no safety; otherwise the template is sent. The Dispatcher builds a barricade list that cannot be sent until a named person approves it.

## Data
Open-Meteo (CC BY 4.0) for rain, Copernicus DEM GLO-30 for low pockets, OpenStreetMap (ODbL) for underpass locations, plus a short curated list of known flood spots.

## Privacy (DPDP Act 2023)
Telegram stores only a chat id and three spot ids for 24 hours. Location is used once and not stored. `/stop` erases the record. The web app's location button runs in the browser only. This is design intent, not legal advice.

## Honest results
- Backtest on [DATE] for [N] reported flood events: precision [X], recall [Y], first warning [Z] minutes before the reported start. Source of each event: [URLs]. Thresholds in `risk.py` were [not tuned / tuned on the same day, so treat results as optimistic].
- Limits: 30 m elevation data is coarse in a flat city, so pocket depth ranks spots rather than measuring water depth. Rain data is modelled, not a sensor at the underpass. This is guidance, not a guarantee.

## AI tools used
Claude (Anthropic) assisted with planning and writing code and tests. [Add any other tool you used.]

## Run it
`docs/DEPLOY.md`. Tests: `pytest` (36+).
