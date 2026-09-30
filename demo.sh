#!/usr/bin/env bash
# One-command public demo: Ollama (Qwen) + FastAPI + Next.js on this Mac, shared via two
# Cloudflare quick tunnels. Ollama itself is never exposed — only the API and the website.
#
#   ./demo.sh          start everything, print the public link, Ctrl+C to stop
#
# Needs: ollama, cloudflared (brew install cloudflared), pnpm, .venv with requirements.
# Tunnels use HTTP/2 over TCP 443 because many campus/office networks block QUIC (UDP).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOGS="$ROOT/results/demo_logs"
MODEL="${LOCAL_LLM_MODEL:-hf.co/Sagnik120/agrivision-qwen-gguf:Q8_0}"
ENV_LOCAL="$ROOT/frontend/.env.local"
mkdir -p "$LOGS"
PIDS=()

say()  { printf "\033[1;32m▸\033[0m %s\n" "$*"; }
fail() { printf "\033[1;31m✗ %s\033[0m\n" "$*" >&2; exit 1; }

cleanup() {
  echo
  say "Stopping demo…"
  for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null || true; done
  # Local dev should go back to auto-detecting the API host.
  [[ -f "$ENV_LOCAL.demo-backup" ]] && mv "$ENV_LOCAL.demo-backup" "$ENV_LOCAL" || rm -f "$ENV_LOCAL"
  say "Stopped. Logs are in results/demo_logs/"
}
trap cleanup EXIT INT TERM

port_busy() { lsof -iTCP:"$1" -sTCP:LISTEN -t >/dev/null 2>&1; }

# Wait for "https://….trycloudflare.com" to appear in a cloudflared log.
tunnel_url() {
  local log="$1" url=""
  for _ in $(seq 1 60); do
    url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$log" | head -1 || true)
    [[ -n "$url" ]] && { echo "$url"; return; }
    sleep 1
  done
  fail "Tunnel did not start — see $log"
}

wait_http() {
  for _ in $(seq 1 "${2:-90}"); do curl -fs -o /dev/null "$1" && return; sleep 1; done
  fail "$1 did not come up"
}

# ---- preflight --------------------------------------------------------------
command -v cloudflared >/dev/null || fail "cloudflared missing: brew install cloudflared"
command -v ollama      >/dev/null || fail "ollama missing: https://ollama.com/download"
command -v pnpm        >/dev/null || fail "pnpm missing: npm i -g pnpm"
[[ -x "$ROOT/.venv/bin/uvicorn" ]] || fail ".venv not set up (pip install -r requirements.txt)"
for p in 8000 3000; do
  port_busy "$p" && fail "Port $p is in use — stop your dev servers (uvicorn / pnpm dev) first"
done

# ---- 1. Qwen via Ollama (local only) ----------------------------------------
if ! curl -fs -o /dev/null http://localhost:11434/api/version; then
  say "Starting Ollama…"
  (ollama serve >"$LOGS/ollama.log" 2>&1 &) ; wait_http http://localhost:11434/api/version 30
fi
# Capture first: with pipefail, `ollama list | grep -q` fails when grep exits early (SIGPIPE).
MODELS="$(ollama list)"
grep -qF "$MODEL" <<<"$MODELS" || { say "Pulling $MODEL (one time)…"; ollama pull "$MODEL"; }
say "Warming up Qwen…"
curl -fs http://localhost:11434/api/generate -d "{\"model\":\"$MODEL\",\"prompt\":\"hi\",\"stream\":false,\"keep_alive\":\"2h\"}" -o /dev/null \
  || fail "Ollama could not run $MODEL"

# ---- 2. API -----------------------------------------------------------------
say "Starting API on :8000…"
(cd "$ROOT" && exec .venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 >"$LOGS/api.log" 2>&1) &
PIDS+=($!)
wait_http http://localhost:8000/api/v1/health 120

say "Opening API tunnel…"
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:8000 >"$LOGS/tunnel-api.log" 2>&1 &
PIDS+=($!)
API_URL=$(tunnel_url "$LOGS/tunnel-api.log")
say "API is public at $API_URL"

# ---- 3. Website (production build pointing at the API tunnel) ---------------
[[ -f "$ENV_LOCAL" ]] && cp "$ENV_LOCAL" "$ENV_LOCAL.demo-backup"
echo "NEXT_PUBLIC_API_URL=$API_URL" >"$ENV_LOCAL"
say "Building website (about a minute)…"
(cd "$ROOT/frontend" && pnpm build >"$LOGS/web-build.log" 2>&1) || fail "Build failed — see $LOGS/web-build.log"
(cd "$ROOT/frontend" && exec pnpm start -p 3000 >"$LOGS/web.log" 2>&1) &
PIDS+=($!)
wait_http http://localhost:3000 60

say "Opening website tunnel…"
cloudflared tunnel --no-autoupdate --protocol http2 --url http://localhost:3000 >"$LOGS/tunnel-web.log" 2>&1 &
PIDS+=($!)
WEB_URL=$(tunnel_url "$LOGS/tunnel-web.log")

# New tunnel hostnames can take 1-2 minutes to resolve on some networks (seen ~80s on campus Wi-Fi).
say "Waiting for the public links to resolve (up to ~3 min)…"
for _ in $(seq 1 60); do
  curl -fs -m 5 -o /dev/null "$API_URL/api/v1/health" && curl -fs -m 5 -o /dev/null "$WEB_URL" && break
  sleep 3
done

cat <<EOF

  ┌─────────────────────────────────────────────────────────────────────┐
    Agri-Vision demo is live

    Share this link:  $WEB_URL
    Admin portal:     $WEB_URL/login?role=admin

    API:  $API_URL   (Ollama/Qwen stays private on this Mac)
    Keep this window open and the Mac plugged in. Ctrl+C to stop.
  └─────────────────────────────────────────────────────────────────────┘

EOF
command -v qrencode >/dev/null && qrencode -t ANSIUTF8 "$WEB_URL" || true

# Keep the Mac awake for as long as the demo runs.
caffeinate -dis -w $$ &
PIDS+=($!)
wait "${PIDS[0]}"
