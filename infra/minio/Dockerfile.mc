FROM golang:1.25-alpine AS build
RUN CGO_ENABLED=0 go install github.com/minio/mc@v0.0.0-20250813083541-7394ce0dd2a8
FROM alpine:3.22
RUN apk add --no-cache ca-certificates && addgroup -g 10001 minio && adduser -D -u 10001 -G minio minio
COPY --from=build /go/bin/mc /usr/local/bin/mc
USER 10001:10001
ENTRYPOINT ["mc"]
