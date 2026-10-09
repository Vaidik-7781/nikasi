#!/usr/bin/env bash
# One-command deploy. Run in AWS CloudShell or any shell logged in to a STANDALONE AWS account.
# Needs: aws cli, sam cli (pip install aws-sam-cli). Telegram stays off until you set the secret (docs/DEPLOY.md).
set -euo pipefail
STACK=${STACK:-nikasi}; REGION=${REGION:-ap-south-1}
sam build -t infra/template.yaml
sam deploy --stack-name "$STACK" --region "$REGION" --resolve-s3 --capabilities CAPABILITY_IAM \
  --no-confirm-changeset --no-fail-on-empty-changeset ${PARAMS:+--parameter-overrides $PARAMS}
out() { aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }
API=$(out ApiUrl); BUCKET=$(out WebBucketName); WEB=$(out WebUrl); LOGIN=$(out WardLoginDomain); CLIENT=$(out WardClientId); POOL=$(out WardPoolId)
mkdir -p .build && printf 'window.NIKASI_API = "%s";\nwindow.NIKASI_COGNITO = {domain: "%s", clientId: "%s"};\n' "$API" "$LOGIN" "$CLIENT" > .build/config.js
aws s3 sync web "s3://$BUCKET" --exclude config.js --exclude mock_state.json --delete --region "$REGION"
aws s3 cp .build/config.js "s3://$BUCKET/config.js" --region "$REGION" --cache-control no-cache
aws s3 cp web/mock_state.json "s3://$BUCKET/mock_state.json" --region "$REGION"
echo "API: $API"; echo "WEB: $WEB"; echo "CONSOLE: $WEB/console.html"
echo "Create a ward user: aws cognito-idp admin-create-user --user-pool-id $POOL --username <email> --region $REGION"
echo "Smoke test: curl -s $API | head -c 400"
echo "Run the risk engine once now: aws lambda invoke --function-name \$(aws cloudformation describe-stack-resource --stack-name $STACK --logical-resource-id RiskEngine --query StackResourceDetail.PhysicalResourceId --output text --region $REGION) --region $REGION /dev/stdout"
