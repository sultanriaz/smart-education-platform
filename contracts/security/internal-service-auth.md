# Internal Service Authentication

Sprint 16 defines short-lived signed internal service tokens.

## Algorithm

`EdDSA` using an Ed25519 key pair per service.

Each service keeps its private key only in deployment secrets. Other services
receive only the public key.

## Required claims

```text
iss = smart-education-internal
sub = calling service name
aud = target service name
iat
nbf
exp
jti
scope[]
token_type = service
correlation_id
```

Default token TTL should be approximately 60 seconds.

## Authorization

The target service verifies:

1. signature using the calling service's trusted public key
2. issuer
3. audience
4. token type
5. expiry
6. required scopes
7. correlation header/token consistency

Example scope:

```text
notifications.events.write
academic.rosters.read
platform.audit.write
```

## Migration from existing static internal tokens

Existing `INTERNAL_SERVICE_TOKEN`/`INTERNAL_EVENT_TOKEN` values may be retained
for a short local migration window, but production should converge on signed,
short-lived tokens.

Do not reuse user JWT signing keys for internal service identity.

Do not expose internal private keys through Platform settings, frontend runtime
configuration, Git, images, or Compose files.
