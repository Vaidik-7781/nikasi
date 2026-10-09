# Architecture

```mermaid
flowchart LR
  subgraph Sources
    OM[Open-Meteo rain] --- DEM[Copernicus DEM] --- OSM[OpenStreetMap]
  end
  EB[EventBridge every 15 min] --> RE[Lambda: risk engine]
  Sources -.-> RE
  RE --> G[Agent graph: Sentinel, Verifier, Alerter]
  G --> ST[(DynamoDB state, TTL)]
  G -->|action changed| Q[SQS alerts + DLQ]
  Q --> SN[Lambda sender] --> TG[Telegram]
  BR[Bedrock + Guardrails, optional] -.reword only.-> G
  ST --> API[API Gateway + Lambda read API] --> WEB[S3 + CloudFront web app, offline]
  ST --> OPS[Lambda ward ops] --> DT[(DynamoDB dispatch log)]
  COG[Cognito JWT] --> OPS
  CW[CloudWatch alarms] --> SNS[SNS email]
```

## Safety rules (each has a test)
1. Missing or old data is UNKNOWN and acts as NO-GO (engine, API 404, browser, bot).
2. Worse is accepted at once; better must hold two readings (Verifier).
3. A model may only reword. Its text is dropped unless it keeps the verdict word, adds no new number and claims no safety. Never asked about UNKNOWN.
4. A dispatch list cannot be sent without a named approver, taken from the verified token, and approval is rejected if conditions changed since the person looked.
5. Telegram keeps a chat id and 3 spot ids for 24 h; `/stop` erases; location is not stored.

## Not built
Multi-city, photo reports, route-level check, SACHET/IMD alert feed, real sending of an approved dispatch list (it is recorded, not transmitted).
