# Demo video script (target 2:40, hard limit 3:00)

The video must SHOW AWS, not just say it. Record at 1080p, upload to YouTube as unlisted, then open the link in a private window to confirm.

| Time | Screen | Say |
|---|---|---|
| 0:00-0:15 | A news headline photo or clip of a flooded underpass (use one you have rights to), then the Nikasi map | "Every monsoon people drive into flooded underpasses. Nikasi tells you go, caution or no-go for the specific underpass, and how long you have." |
| 0:15-0:55 | Web app on the CloudFront URL: tap a CAUTION card, show the countdown, the reasons, the nearest-to-me button | "Each card is one underpass. Rain, terrain and known flood history give a state every 15 minutes. This one turns no-go in about [N] minutes." |
| 0:55-1:25 | Disconnect network / stale data: card flips to UNKNOWN | "If data is old or missing it says UNKNOWN and means NO-GO. It never shows an old green." |
| 1:25-1:55 | Phone: Telegram alert arriving after a state change | "Share your location once and you get an alert when a nearby underpass changes. We store a chat id for 24 hours and erase it on /stop." |
| 1:55-2:25 | AWS console tabs: CloudFormation stack, Lambda + EventBridge schedule, DynamoDB items, SQS and DLQ, CloudFront | "It runs on AWS: EventBridge triggers Lambda every 15 minutes, state lives in DynamoDB, alerts go through SQS with a dead-letter queue, the app is served from S3 and CloudFront." |
| 2:25-2:50 | Backtest table (real numbers only) and the agent graph diagram | "We replayed [DATE] rain through the engine: [precision/recall/lead time]. A model can reword alerts but cannot change a state, and a dispatch list needs a human to approve." |

Do not claim anything the video does not show.
