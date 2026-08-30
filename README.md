# Boop on Railway

[Boop](https://github.com/chrisgreg/boop) is a tiny, self-hosted notification inbox for developers. Your apps `POST` an event to one endpoint; Boop stores it and pushes it to your phone through Apple Push Notifications. There is no hosted relay, account system, or telemetry.

This repository is a [Railway](https://railway.com) template wrapper. It vendors the upstream `server/` source at a pinned release and adds nothing else: no forks, no patches, no configuration generation.

## What this template deploys

| Service | Source | Version |
| --- | --- | --- |
| `boop` (Go server + embedded web UI) | this repo, `/server` | upstream [`v1.3.0`](https://github.com/chrisgreg/boop/releases/tag/v1.3.0), commit `881004d8ed6fb9be1a3812ff779119ba04b0d542` |

Topology: one public service with one Railway volume mounted at `/data` holding the SQLite database (`boop.db`, WAL mode). No other services are required.

## Post-deploy setup

1. Open your Railway domain. The first visit starts the setup wizard (server check, APNs, pairing, first project, test notification).
2. Sign in to the web UI with the `BOOP_ADMIN_USER` / `BOOP_ADMIN_PASSWORD` values you set at deploy time.
3. Create a project in the web UI and copy its API key (shown once).
4. Send an event:

```bash
curl https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/v1/events \
  -H "Authorization: Bearer boop_proj_..." -H "Content-Type: application/json" \
  -d '{"title": "Backup complete", "level": "success"}'
```

5. **Push notifications (optional):** create an APNs key in your Apple Developer account, then set `APNS_TEAM_ID`, `APNS_KEY_ID`, `APNS_BUNDLE_ID`, and `APNS_PRIVATE_KEY` (base64 of your `.p8`). Boop runs fully without them — events are stored and shown in the web inbox, pushes are skipped.
6. **iOS app:** you build and sign it yourself from [`chrisgreg/boop/ios`](https://github.com/chrisgreg/boop/tree/v1.3.0/ios) with your own Apple Developer account, then pair it with the QR code from the web UI. See the upstream [ios/README.md](https://github.com/chrisgreg/boop/blob/v1.3.0/ios/README.md).

## Important limitations

- **There is no official Boop container image.** Upstream publishes binaries only, so this template builds the server from the vendored source using the unmodified upstream `server/Dockerfile` (multi-stage: Node 24 → Go 1.27 → Alpine 3.21).
- **Push delivery requires a self-built iOS app.** This is inherent to Boop, not to Railway: the server ships the inbox and API regardless. The web UI works standalone.
- `BOOP_BASE_URL` is set automatically to your Railway public domain. If you attach a custom domain, update it.

## Updating

Upstream is pinned to `v1.3.0` in this repository; updating is a deliberate bump: replace `server/` with the new tag's tree, update the version references in this README, and push. The template deploys from this repository, so it will not drift on its own.

## Differences from upstream

The vendored tree is byte-identical to upstream `v1.3.0` except for two Railway-compatibility changes in `server/`, each commented in place:

1. **`server/Dockerfile`:** the upstream `VOLUME ["/data"]` declaration is removed, because Railway's builder rejects Docker `VOLUME` directives. Persistence is unchanged in practice: a Railway volume is mounted at `/data`.
2. **`server/Dockerfile` + `server/entrypoint.sh` (new):** Railway mounts volumes root-owned, so the container starts as root, `chown`s `/data` to uid 1000, then drops to uid 1000 via `su-exec` — preserving the upstream image's non-root runtime posture. When started as a non-root user (e.g. plain `docker compose` on a pre-owned host directory), the entrypoint execs the server directly, matching upstream behavior.

Everything else — Go source, migrations, and the embedded web UI — is unmodified upstream code.

## Provenance and license

- Upstream: https://github.com/chrisgreg/boop
- Pinned source: tag [`v1.3.0`](https://github.com/chrisgreg/boop/releases/tag/v1.3.0), commit `881004d8ed6fb9be1a3812ff779119ba04b0d542`
- License: MIT (upstream `LICENSE` is preserved verbatim at the repository root)
- `server/` is an unmodified copy of upstream `server/` at the pinned commit; `UPSTREAM_CHANGELOG.md` is the upstream changelog
- `icon.png` is the unchanged first-party logo from upstream `docs/boop.png`
