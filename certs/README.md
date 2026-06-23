# Cloudflare Origin Certificate (Phase B TLS)
#
# Do not commit PEM files. On the VPS:
#
# 1. Cloudflare → SSL/TLS → Origin Server → Create certificate
#    Hostnames: marketstructureos.com, *.marketstructureos.com
# 2. Save as:
#      certs/cloudflare-origin.pem
#      certs/cloudflare-origin-key.pem
#    chmod 600 certs/cloudflare-origin-key.pem
# 3. In repo-root .env on the VPS:
#      PPE_CADDYFILE=./Caddyfile.tls
# 4. Cloudflare → SSL/TLS → Overview → **Full (strict)**
# 5. docker compose up -d caddy
#
# Phase A (Flexible, HTTP origin): leave PPE_CADDYFILE unset — uses ./Caddyfile.
