#!/bin/sh
set -e

SSL_DIR="/etc/nginx/ssl"
CERT="$SSL_DIR/fullchain.pem"
KEY="$SSL_DIR/privkey.pem"

if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
    echo "No SSL certificates found. Generating self-signed..."
    mkdir -p "$SSL_DIR"
    openssl req -x509 -nodes -days 365 \
        -newkey rsa:2048 \
        -keyout "$KEY" \
        -out "$CERT" \
        -subj "/C=US/ST=State/L=City/O=CyberPath/CN=localhost" \
        2>/dev/null
    echo "Self-signed certificate generated."
fi

exec nginx -g "daemon off;"
