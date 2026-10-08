# RabbitMQ Metrics

RabbitMQ's built-in Prometheus plugin should expose:

```text
:15692/metrics
```

Enable it in the Sprint 17 broker image/config:

```text
rabbitmq-plugins enable --offline rabbitmq_prometheus
```

Do this through the actual RabbitMQ image/config used by the repository rather
than running an ad-hoc command after every container restart.

Prometheus already contains a `rabbitmq:15692` scrape target.

Do not expose port 15692 publicly.
