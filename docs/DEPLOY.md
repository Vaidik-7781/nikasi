# Deploy (about 10 minutes)

1. Use a standalone AWS account (not one under an organisation policy that blocks DynamoDB, SQS or S3).
2. Open CloudShell, region Mumbai (ap-south-1).
3. `git clone https://github.com/Vaidik-7781/nikasi && cd nikasi`
4. `pip install --user aws-sam-cli && bash scripts/deploy.sh`
5. Open the printed WEB URL. First data appears within 15 minutes, or run the Lambda once with the printed command.
6. Set an AWS Budget alert (Billing, Budgets) before leaving it running.

## Ward console
After deploy, `deploy.sh` prints a CONSOLE URL and the command to create a ward user (email login, admin-created only). Sign in, review the proposed list, approve.
Optional: `PARAMS="AlarmEmail=you@example.com" bash scripts/deploy.sh` for alarm emails (confirm the subscription mail).

## Optional: Telegram alerts
1. In Telegram, talk to @BotFather, create a bot, copy the token.
2. Secrets Manager, new secret named `nikasi/telegram`, JSON: `{"token":"<bot token>","webhook_secret":"<long random string>"}`.
3. `sam deploy ... --parameter-overrides EnableTelegram=true` (or run `PARAMS="EnableTelegram=true" bash scripts/deploy.sh`).
4. Set the webhook, replacing the three values:
   `curl "https://api.telegram.org/bot<TOKEN>/setWebhook" -d "url=<TelegramWebhookUrl output>" -d "secret_token=<webhook_secret>"`

## Optional: model-worded alerts
Set `BEDROCK_MODEL_ID` (and `GUARDRAIL_ID`) on the RiskEngine function. Without them alerts use the fixed templates. Check the model is available in your region first.

## Before the demo
- `pip install rasterio numpy` then run `scripts/osm_underpasses.py`, `scripts/dem_pockets.py`, `scripts/build_spots.py` on a machine with internet, review the spots on a map, commit `src/nikasi/spots.json`.
- Fill `data/flood_events.json` from real reports (with source URLs), then run `scripts/backtest.py`.
