# Slack Integration Setup

## 1. Create Slack App
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "VANTAGE AI Alerts"
5. Select your workspace

## 2. Configure Webhook
1. Go to "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to On
3. Click "Add New Webhook to Workspace"
4. Select the channel for alerts
5. Copy the webhook URL

## 3. Update AlertManager
Replace `YOUR_SLACK_WEBHOOK_URL` in `monitoring/alertmanager.yml` with your webhook URL.

## 4. Test Integration
Run: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test alert from VANTAGE AI"}' YOUR_SLACK_WEBHOOK_URL`
