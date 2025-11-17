#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API="$BASE_URL/api/v1"

echo "== SautiAI Smoke Test =="
echo "-- health"
curl -sS "$BASE_URL/health" | jq . || curl -sS "$BASE_URL/health"

echo "-- insights"
curl -sS "$API/dashboard/insights?days=7" | jq '.success,.message' || true

echo "-- trends"
curl -sS "$API/dashboard/sentiment-trends?days=7" | jq '.success,.data.period_days' || true

echo "-- search (q=road)"
curl -sS "$API/search/feedback?q=road&limit=3" | jq '.success, (.data|length), (.data[0]|{whyMatched,highlights})' || true

echo "-- alerts list"
curl -sS "$API/alerts" | jq '.success, (.data|length)' || true

echo "-- rules list"
curl -sS "$API/rules" | jq '.success, (.data|length)' || true

echo "-- agents types"
curl -sS "$API/agents/types" | jq '.success,.data' || true

echo "-- ai analyze (fallback-friendly)"
curl -sS -X POST "$API/ai/analyze-sentiment" -H "Content-Type: application/json" \
  -d '{"feedback_id":"test","text":"Hospital service is terrible and slow","language":"en"}' \
  | jq '.success,.data.sentiment' || true

echo "-- ai classify (fallback-friendly)"
curl -sS -X POST "$API/ai/classify-sector" -H "Content-Type: application/json" \
  -d '{"feedback_id":"test","text":"The school lacks textbooks and teachers","language":"en"}' \
  | jq '.success,.data.primary_sector,.data.category' || true

echo "== Done =="


