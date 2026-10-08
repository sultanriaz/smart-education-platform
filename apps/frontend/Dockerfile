FROM node:22-alpine AS build

WORKDIR /app

COPY package.json ./
COPY package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci --ignore-scripts --no-audit --no-fund; \
    else \
      npm install --ignore-scripts --no-audit --no-fund; \
    fi

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/40-runtime-config.sh /docker-entrypoint.d/40-runtime-config.sh
COPY docker/45-security-headers.sh /docker-entrypoint.d/45-security-headers.sh

USER root
RUN chmod +x \
      /docker-entrypoint.d/40-runtime-config.sh \
      /docker-entrypoint.d/45-security-headers.sh \
    && mkdir -p /etc/nginx/security \
    && chown -R 101:101 /etc/nginx/security /usr/share/nginx/html
USER 101:101

COPY --from=build --chown=101:101 /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget -qO- http://127.0.0.1:8080/health >/dev/null || exit 1
