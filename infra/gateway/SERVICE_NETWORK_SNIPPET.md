# Attach every public backend service to the shared edge network

Each service's API container must join the external network:

```yaml
services:
  <service-name>:
    networks:
      - default
      - smart-education-edge

networks:
  smart-education-edge:
    external: true
    name: smart-education-edge
```

Only API containers need the edge network. Databases, Redis instances, workers,
MinIO, migration containers, etc. should remain on private Compose networks
unless there is a specific reason otherwise.

Expected DNS names on `smart-education-edge`:

- identity-service
- academic-service
- attendance-service
- scheduling-service
- notification-service
- facility-service
- learning-service
- assessment-service
- reporting-service
- platform-service

If the actual Compose service names differ, update the gateway upstream environment
variables instead of creating aliases casually.
