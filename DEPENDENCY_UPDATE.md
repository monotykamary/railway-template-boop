# Dependency candidate — 2026-11-15

Keep the upstream Boop 1.3.0 application unchanged. Advance the build stages to Node 24.22.3 and Go 1.27.4, using exact registry digests and official stable/security release evidence. Retain the existing Alpine 3.24.3 runtime digest: this candidate does not silently roll the operating-system base. Every production FROM remains version/digest-pinned.

The Go API/auth test packages run during the candidate image build. The product smoke logs into the real administrator API, creates a notification-disabled project, ingests an event using its project key, rejects invalid login and ingestion credentials, and retrieves the exact boot-created records after upgrade/redeploy without recreating them. External Apple push delivery is not certified. All local persistence and live Railway release gates remain mandatory.
