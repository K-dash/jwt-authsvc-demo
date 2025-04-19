#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# RSA2048 鍵ペアを生成し、infra/secrets/ 配下へ配置する
# -----------------------------------------------------------------------------
set -euo pipefail

KEY_DIR="$(cd "$(dirname "$0")/../secrets" && pwd)"
mkdir -p "${KEY_DIR}"

PRIVATE_KEY="${KEY_DIR}/auth_private_key.pem"
PUBLIC_KEY="${KEY_DIR}/auth_public_key.pem"

# 既存鍵があれば退避
for f in "$PRIVATE_KEY" "$PUBLIC_KEY"; do
    [[ -f "$f" ]] && mv "$f" "${f}.bak_$(date +%s).pem"
done

echo "▶ Generating 2048‑bit RSA key pair …"
openssl genrsa -out "$PRIVATE_KEY" 2048 >/dev/null 2>&1
openssl rsa -in  "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY" >/dev/null 2>&1

chmod 600 "$PRIVATE_KEY" "$PUBLIC_KEY"

echo "✅  Done."
echo "  Private: $PRIVATE_KEY"
echo "  Public : $PUBLIC_KEY"
