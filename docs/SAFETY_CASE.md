# Safety case

Nikasi advises people near floodwater, so the question is not "does it work" but "how does it fail". Each hazard below names the control and the test that proves it. Run them all with `pytest`.

| # | Hazard | Control | Test |
|---|---|---|---|
| 1 | Weather feed down or empty, app shows an old green | Missing or older than 45 min = UNKNOWN, acts as NO-GO | `test_missing_weather_is_unknown_and_acts_as_no_go`, `test_stale_weather_is_unknown`, `test_every_spot_is_never_green_without_fresh_data` |
| 2 | Bad timestamp (future clock) looks fresh | More than 5 min in the future = UNKNOWN | `test_future_timestamp_is_unknown` |
| 3 | Lambda cannot fetch weather | Writes UNKNOWN rows instead of skipping | `test_handler_writes_unknown_when_fetch_fails` |
| 4 | API asked for a spot with no row | 404 that says UNKNOWN / NO-GO, never an empty "fine" | `test_api_missing_spot_fails_safe` |
| 5 | Alerts flap or lift a warning too early | Worse is accepted at once; better must hold one more 15-min reading | `test_worse_passes_immediately`, `test_better_is_held_one_cycle_then_accepted` |
| 6 | Language model says "it is safe" or invents a number | Reworded text is used only if it keeps the verdict word, adds no new number, claims no safety, fits 280 chars; else the fixed template | `test_model_text_rejected`, `test_bad_model_falls_back_to_template`, `test_bad_model_text_is_dropped_but_alert_still_sent` |
| 7 | Model is down or errors | Fixed template is sent; alerts never depend on a model | `test_model_exception_falls_back`, `test_template_used_without_model` |
| 8 | Model asked to explain missing data | Never asked about UNKNOWN | `test_model_never_asked_about_unknown`, `test_unknown_alert_is_never_model_written` |
| 9 | A barricade list is acted on without a person deciding | Needs a signed-in user; approver name comes from the verified token, not the request body; rejected if conditions changed since the person looked | `test_requires_signed_in_user`, `test_approval_records_token_identity_not_body`, `test_stale_review_is_rejected`, `test_dispatch_needs_named_approval` |
| 10 | Duplicate or spammy alerts | Alert only when the action changes; sender claims each message id once | `test_graph_alerts_only_on_action_change`, `test_no_change_no_alert`, `test_sender_is_idempotent` |
| 11 | Personal data kept | Telegram stores chat id + 3 spot ids for 24 h; location is used once and dropped; `/stop` erases | `test_stop_erases`, `test_location_subscribes_to_nearest_three_and_missing_state_is_no_go`, `test_start_shows_consent` |
| 12 | Phone is offline and shows a cached green | The browser re-checks age itself; rows over 45 min old render UNKNOWN | manual check (`web/app.js`, `effective()`); no automated browser test |
| 13 | Map library or tiles fail to load | Safety cards render without the map | manual check (page rendered with the CDN blocked) |

## What this does not claim
- Thresholds in `src/nikasi/risk.py` are placeholders. They are not calibrated against real flood events (`scripts/backtest.py` exists for that and has not been run on real data).
- 30 m elevation data is coarse in a flat city. Pocket depth ranks spots; it does not measure water depth.
- Rain is modelled (Open-Meteo), not measured at the underpass. There is no water-level sensor.
- The project has not been deployed to AWS. The infrastructure template lints clean and the handlers are unit-tested against fakes.
- Guidance, not a guarantee. If there is water on the road, do not enter.
