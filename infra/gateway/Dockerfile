FROM nginx:1.27-alpine

RUN apk add --no-cache curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY templates /etc/nginx/templates
COPY snippets /etc/nginx/snippets
COPY 19-local-upstreams.envsh /docker-entrypoint.d/19-local-upstreams.envsh
RUN sed -i 's/\r$//' /docker-entrypoint.d/19-local-upstreams.envsh && chmod 755 /docker-entrypoint.d/19-local-upstreams.envsh
RUN chown -R nginx:nginx /etc/nginx /var/cache/nginx /var/log/nginx /var/run
USER nginx

EXPOSE 8080 8443

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8080/health || exit 1
