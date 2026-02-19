# HEARTBEAT.md

Run lightweight checks unless within quiet hours or recently checked (<30m):
- Inbox urgency scan
- Calendar next 24-48h
- Mentions/notifications
- Project repo health (`git status` in active repos)

If nothing actionable: HEARTBEAT_OK
