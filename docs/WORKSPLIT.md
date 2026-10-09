# Work split (4 lanes)

Contract between lanes = the DynamoDB state item (written by `handler.py`):
`{spot_id, name, state, act_as, reasons[], minutes_to_no_go, updated_at, ttl}`
Everyone codes against this. Frontend mocks it from `data/mock_state.json` until the API is live.

## Target tree
```
src/nikasi/
  risk.py            [A] engine (done)         weather.py [A] (done)
  handler.py         [A] cron Lambda (done)    sachet.py  [A] IMD/NDMA CAP feed, optional
  api.py             [A] GET /spots, /spots/{id}  (API Gateway Lambda)
  agents/            [B] Strands graph
    sentinel.py verifier.py alerter.py dispatcher.py templates.py guardrails.py
  telegram_bot.py    [B] /start, share location, /stop (erasure), alerts via SQS sender
  sender.py          [B] SQS consumer, idempotent, DLQ
scripts/
  dem_pockets.py     [C] run, validate  osm_underpasses.py [C] run, snap spots
  backtest.py        [C] one real flood day: precision, recall, lead time
web/                 [D] static PWA (map + GO/CAUTION/NO-GO cards + countdown)
infra/template.yaml  [A] extend: API, SQS+DLQ, SNS, CloudFront, budgets
docs/                [D] README screenshots, architecture, writeup, video script
```

## Lanes
| Lane | Owner | Build order | Done when |
|---|---|---|---|
| A engine + infra | you | deploy SAM; api.py; SQS/DLQ; budget alarm | /spots returns live states from AWS |
| B agents + Telegram | you or friend | templates first, then Strands graph, then bot | alert arrives on phone; model off still sends template |
| C data + backtest | geo/data friend | snap spots; DEM pockets; backtest numbers | table of precision/recall/lead time, honest |
| D frontend + video | design friend | map w/ mock data; cards; offline cache; record video | demo video <3 min shows AWS console + app |

## Timeline (IST)
- Fri: A deploy, C spots + pockets, D map on mock.
- Sat: A api, B templates + bot, C backtest, D wire to API. Freeze midnight.
- Sun AM: video, README, writeup, Builder Center blog. Submit before deadline.
- Cut order if late: photo report, 2nd city, route check, offline PWA, Telegram. Keep backtest + UNKNOWN=NO-GO.
