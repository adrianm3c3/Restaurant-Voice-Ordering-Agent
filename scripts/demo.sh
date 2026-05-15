#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"
SESSION_ID="${SESSION_ID:-demo-script}"

mkdir -p reports

echo "======================================"
echo " Demo Smoke Test"
echo "======================================"

echo "[1/4] Health check..."
curl -fsS "$BASE_URL/health" | tee reports/demo_health.json
echo

echo "[2/4] Add pizza..."
curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"I want a large pepperoni pizza\"}" \
  | tee reports/demo_add_pizza.json
echo

echo "[3/4] Ask total..."
curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"what is my total\"}" \
  | tee reports/demo_total.json
echo

echo "[4/4] RAG menu question..."
curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"text\":\"Do you have vegetarian pizzas?\"}" \
  | tee reports/demo_rag.json
echo

echo "Demo smoke test complete."
