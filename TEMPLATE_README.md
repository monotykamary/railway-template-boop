# Deploy and Host Boop on Railway

## About Hosting Boop

Boop is a tiny, self-hosted notification inbox for developers. Your applications `POST` an event to a single API endpoint; the server stores it in SQLite, renders it in a built-in web inbox, and pushes it to your phone through Apple Push Notifications. There is no hosted relay, no account system, and no telemetry — everything runs inside your own Railway project.

This template deploys the Boop server (Go, with the web UI embedded in the binary) pinned to upstream release v1.3.0, with a persistent volume for the database and a health check on `/health`.

## Common Use Cases

- Send yourself a push when a backup, cron job, or CI workflow finishes — from any shell script, GitHub Action, or CI step with one `curl`
- Turn application errors into rich phone notifications with stack traces, tags, context, and breadcrumbs
- Group repeated errors by fingerprint so one problem is one row, not forty-seven pushes
- Give AI agents a read-only MCP endpoint (`/mcp`) over your event inbox
- Keep operational events out of Slack while keeping them reachable on your phone

## Dependencies for Boop Hosting

### Deployment Dependencies

None besides the template itself: one Go server service with one Railway volume. No database service, no queue, no object storage.

Optional: Apple Push Notifications service (APNs). Push delivery needs an APNs key from your Apple Developer account plus a self-built, self-signed iOS app from the upstream repository. Without APNs credentials Boop still stores and displays every event in the web inbox; only the phone push is skipped.

### Implementation Details

- The `boop` service owns the public domain; all browser traffic, the API (`/api/v1/events`), and the MCP endpoint go through the same origin.
- `BOOP_BASE_URL` is generated automatically from the service's public domain and is what your phone uses to reach the server. If you attach a custom domain, update this variable.
- `BOOP_ADMIN_USER` and `BOOP_ADMIN_PASSWORD` protect the web UI and admin API. `BOOP_ADMIN_PASSWORD` is generated at deploy time (8+ characters). Leave both blank only if you understand that the web UI would then be public.
- `BOOP_MCP_TOKEN` is optional; it guards the read-only MCP endpoint for AI agents.
- Data lives in the SQLite file at `/data/boop.db` (WAL mode). The volume is included in daily backups.
- Retention defaults to 90 days of event history (`BOOP_RETENTION_DAYS`, `0` keeps everything).
- APNs variables are optional and safe to leave empty at deploy time. If you add them later, paste the base64 of your `.p8` key into `APNS_PRIVATE_KEY` and leave `APNS_PRIVATE_KEY_PATH` empty.

### Why Deploy Boop on Railway on Railway?

One container, one volume, no external services: a deploy takes about a minute and the free-tier-friendly footprint stays tiny. Railway gives you the public HTTPS domain your phone needs, daily volume backups for the SQLite file, and instant redeploys when you bump the pinned upstream version. Because the whole state is one file, backing up or moving your inbox is trivial.
