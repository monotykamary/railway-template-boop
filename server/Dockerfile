# syntax=docker/dockerfile:1

# ---- web: build the Svelte UI ----
FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS web
WORKDIR /src
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web .
RUN npm run build
# vite writes to ../internal/web/dist relative to /src/web; with WORKDIR /src that is /internal/web/dist.

# ---- build: compile the Go binary with the UI embedded ----
FROM golang:1.27.3-alpine@sha256:b8c9b82affbbb82a020bbcf998dad2ba9516944ac7e883524642a481a9505e9c AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
COPY --from=web /internal/web/dist ./internal/web/dist
ARG VERSION=1.3.0
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X github.com/chrisgreg/boop/server/internal/api.Version=${VERSION}" -o /boop ./cmd/boop

# ---- runtime: binary + CA certificates only ----
FROM alpine:3.21.8@sha256:ce64758a109eb420d874a118f87920e625e12d3634e03b4a5573fd9f6e5d3507
RUN apk add --no-cache ca-certificates tzdata su-exec && adduser -D -u 1000 boop && mkdir -p /data && chown boop:boop /data
COPY --from=build /boop /usr/local/bin/boop
# Railway adapter: the upstream `VOLUME ["/data"]` declaration is removed because
# Railway's builder rejects Docker VOLUME directives. Persistence is provided by
# a Railway volume mounted at /data.
# Railway adapter: the container starts as root so the entrypoint can make the
# root-owned mounted volume writable, then drops to uid 1000 via su-exec. This
# preserves the upstream image's non-root runtime posture.
EXPOSE 8080
ENV BOOP_PORT=8080 BOOP_DATABASE_PATH=/data/boop.db
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/health || exit 1
COPY --chmod=0755 entrypoint.sh /usr/local/bin/entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]
