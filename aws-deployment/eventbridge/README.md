# EventBridge Scheduled Rules

This directory contains configuration files for AWS EventBridge scheduled rules used to trigger automation tasks.

## Files

| File | Purpose |
|------|---------|
| `daily-briefing-schedule.json` | Schedule rule configuration (cron expression) |
| `daily-briefing-targets.json` | Target configuration (API endpoint) |
| `auto-fetch-targets.json` | Legacy auto-fetch ECS task targets |

## Daily Briefing Schedule

The Daily Briefing automation is triggered automatically via EventBridge at:

- **Schedule**: `cron(0 1 ? * MON-FRI *)`
- **Time**: 01:00 UTC = **09:00 HKT** (Hong Kong Time)
- **Days**: Monday through Friday (weekdays only)

## Deployment

### Using the Deployment Script

```bash
# Create EventBridge rule
python3 scripts/active/deployment/setup_eventbridge_schedules.py create

# Check status
python3 scripts/active/deployment/setup_eventbridge_schedules.py status

# Manual trigger (for testing)
python3 scripts/active/deployment/setup_eventbridge_schedules.py trigger

# Disable (without deleting)
python3 scripts/active/deployment/setup_eventbridge_schedules.py disable

# Enable again
python3 scripts/active/deployment/setup_eventbridge_schedules.py enable

# Delete the rule
python3 scripts/active/deployment/setup_eventbridge_schedules.py delete
```

### Manual AWS CLI Commands

```bash
# Create the rule
aws events put-rule \
  --name daily-briefing-schedule \
  --schedule-expression "cron(0 1 ? * MON-FRI *)" \
  --state ENABLED \
  --description "Trigger Daily Briefing at 09:00 HKT on weekdays" \
  --region ap-east-1

# Add target
aws events put-targets \
  --rule daily-briefing-schedule \
  --targets file://aws-deployment/eventbridge/daily-briefing-targets.json \
  --region ap-east-1

# Check rule status
aws events describe-rule \
  --name daily-briefing-schedule \
  --region ap-east-1

# List targets
aws events list-targets-by-rule \
  --rule daily-briefing-schedule \
  --region ap-east-1
```

## Architecture

```
EventBridge Scheduler
         │
         ▼ (01:00 UTC / 09:00 HKT)
┌─────────────────────────┐
│ API Destination         │
│ POST /api/automation/   │
│      tasks/daily-       │
│      briefing/trigger/  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Django API (ECS)        │
│ Creates AutomationTask  │
│ Enqueues Celery Task    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Celery Worker (ECS)     │
│ Stage 1: Scrape data    │
│ Stage 2: Generate AI    │
│          report         │
└─────────────────────────┘
```

## IAM Roles

The EventBridge rule requires the following IAM role:

- **Role Name**: `EventBridgeAutomationRole`
- **Trust Policy**: `events.amazonaws.com`
- **Permissions**: `events:InvokeApiDestination`

## Monitoring

### CloudWatch Metrics

- `AWS/Events/Invocations` - Number of rule invocations
- `AWS/Events/FailedInvocations` - Failed invocations
- `AWS/Events/TriggeredRules` - Rules that matched events

### Logs

Check the following log groups for troubleshooting:

- `/aws/events/daily-briefing-schedule` - EventBridge logs
- `/ecs/mem-dashboard-api` - Django API logs
- `/ecs/alfie-automation-worker` - Celery Worker logs

## Retry Policy

The target has the following retry policy:

- **Maximum Retry Attempts**: 3
- **Maximum Event Age**: 3600 seconds (1 hour)

If all retries fail, the event is sent to a dead-letter queue (if configured).

## Timezone Reference

| Timezone | Time | Day |
|----------|------|-----|
| UTC | 01:00 | MON-FRI |
| HKT (Asia/Hong_Kong) | 09:00 | MON-FRI |
| EST (America/New_York) | 20:00 (prev day) | SUN-THU |
| PST (America/Los_Angeles) | 17:00 (prev day) | SUN-THU |
