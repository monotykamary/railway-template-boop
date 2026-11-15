# syntax=docker/dockerfile:1

# ---- web: build the Svelte UI ----
FROM node:24.22.3-alpine@sha256:116b800c3754b440ee0aa3ed2f20f5bf3d99a554bfd9adeea09ea8017f6e85f5 AS web
WORKDIR /src
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web .
RUN npm run build
# vite writes to ../internal/web/dist relative to /src/web; with WORKDIR /src that is /internal/web/dist.

# ---- build: compile the Go binary with the UI embedded ----
FROM golang:1.27.4-alpine@sha256:0a5f7fe796599ff487605987432e7619ae45beeb2fba4c2ce0b907879932aebf AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
COPY --from=web /internal/web/dist ./internal/web/dist
ARG VERSION=1.3.0
RUN CGO_ENABLED=0 go test ./internal/api ./internal/auth \
 && CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X github.com/chrisgreg/boop/server/internal/api.Version=${VERSION}" -o /boop ./cmd/boop

# ---- runtime: binary + CA certificates only ----
FROM alpine:3.24.3@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a
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
