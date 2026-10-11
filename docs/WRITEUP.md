# Nikasi: writeup

Solo build by Vaidik Gupta (team SocialStar), WeMakeDevs x AWS Environmental Hacks, Heat and Water track.

## Problem
Every monsoon, Delhi underpasses such as Minto Bridge fill within minutes and people drive in. City-wide rain alerts do not say whether the one underpass on your route is passable. Nikasi answers one question for a named underpass: go, caution or no-go, and how many minutes until no-go.

## What it does
- Scores each underpass every 15 minutes from rain now, forecast rain for the next two hours, rain in the last 24 hours, how deep the low pocket is, and whether it is a known flood spot.
- Shows GO / CAUTION / NO-GO with a countdown on an offline-capable web app, and sends Telegram alerts when a nearby spot changes.
- Fails safe: missing or old data shows UNKNOWN and is treated as NO-GO in the backend, the API and the browser.
- A ward console proposes a barricade list for NO-GO spots. It cannot be recorded without a signed-in person approving it.

## The idea that matters: a model is never on the safety path
The risk engine and the Verifier are plain, tested code. A language model may reword an alert, but its text is used only if it keeps the verdict word, adds no number that is not in the fixed template, claims nothing is safe, and stays short. Otherwise the fixed template goes out. The model is never asked about missing data. `docs/SAFETY_CASE.md` lists 13 failure modes, the control for each and the test that covers it; the storm replay (`python -m nikasi.replay`) shows a stand-in model trying to say "definitely safe" and being dropped.

## How it is built
| Part | AWS service / tool |
|---|---|
| 15-minute schedule | EventBridge -> Lambda risk engine |
| State | DynamoDB with TTL |
| Read API | API Gateway (HTTP) + Lambda |
| Web app | S3 + CloudFront (private bucket, origin access control) |
| Alerts | SQS with dead-letter queue -> Lambda -> Telegram; Secrets Manager for the bot token |
| Ward console | Cognito JWT authorizer, Lambda, DynamoDB dispatch log |
| Alarms | CloudWatch alarms -> SNS |
| Alert wording (optional) | Amazon Bedrock with Guardrails, or the open-source Strands Agents SDK |
| Infrastructure as code | AWS SAM, `infra/template.yaml` |

## Data
Open-Meteo (CC BY 4.0) for rain, Copernicus DEM GLO-30 for low pockets, OpenStreetMap (ODbL) for underpass locations, plus a short curated list of known flood spots.

## Privacy
Telegram stores a chat id and three spot ids for 24 hours. Location is used once and not stored. `/stop` erases the record. The web app's location button runs only in the browser. Designed in the spirit of the DPDP Act 2023; this is design intent, not legal advice.

## What is real and what is not
- **Tested:** 46 unit tests cover the engine, agents, API, bot, sender, console and storm replay. CI runs them plus `cfn-lint`.
- **Not deployed:** the AWS stack has not been deployed. The template lints clean and the Lambda handlers are tested against fakes, so treat every AWS claim as design, not as a running system.
- **Not validated:** thresholds are placeholders. No real flood events were replayed, so no precision, recall or lead-time figure exists, and none is claimed. `scripts/backtest.py` is ready for real reports in `data/flood_events.json`.
- **Coarse data:** 30 m elevation in a flat city ranks spots rather than measuring water depth. Rain is modelled, not measured at the underpass. Only 3 seed spots ship, with approximate coordinates.
- **Not built:** multi-city, photo reports, route-level check, official alert feeds, and real transmission of an approved dispatch list (it is recorded, not sent).

## AI tools used
Claude (Anthropic) assisted with planning, code and tests, and with this writeup. The design decisions and the choice of what to claim are mine.

## Run it
`python scripts/local_demo.py` (no AWS needed), `pytest`, and `docs/DEPLOY.md` for AWS.
