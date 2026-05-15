#!/usr/bin/env bash
set -euo pipefail

echo "======================================"
echo " CS 6263 Project Preflight"
echo "======================================"

mkdir -p reports

echo "[1/7] Checking required files..."

required_files=(
  "README.md"
  "Dockerfile"
  "docker-compose.yml"
  ".env.example"
  "requirements.txt"
  "docs/SPEC.md"
  "docs/STORIES.md"
  "docs/REPRODUCE.md"
  "docs/DATA.md"
  "docs/MODELS.md"
  "docs/MODEL_CARD.md"
  "docs/LOGGING.md"
  "docs/usage.md"
  "docs/benchmarks.md"
  "grading/manifest.yaml"
  "grading/traceability.yaml"
  "scripts/demo.sh"
  "scripts/regenerate.sh"
  "scripts/regenerate_prompt.md"
)

missing=0

for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "MISSING: $file"
    missing=1
  else
    echo "OK: $file"
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "Preflight failed: missing required files."
  exit 1
fi

echo "[2/7] Checking project folders..."

if [ ! -d "src" ]; then
  echo "MISSING: src/"
  exit 1
fi

if [ ! -d "tests" ]; then
  echo "MISSING: tests/"
  exit 1
fi

echo "[3/7] Building Docker image..."
docker compose build

echo "[4/7] Starting Docker services..."
docker compose up -d

echo "[5/7] Waiting for health endpoint..."

for i in {1..30}; do
  if curl -fsS http://127.0.0.1:5000/health > reports/health.json; then
    echo "Health check passed."
    break
  fi

  if [ "$i" -eq 30 ]; then
    echo "Health check failed after 30 attempts."
    docker compose logs || true
    exit 1
  fi

  sleep 2
done

echo "[6/7] Running tests..."

docker compose exec app pytest tests \
  --junitxml=reports/user_stories.xml \
  --cov=src \
  --cov-report=xml:reports/coverage.xml \
  --cov-report=html:reports/coverage_html \
  -v

echo "[7/7] Running demo smoke test..."
bash scripts/demo.sh

echo "======================================"
echo " Preflight passed."
echo "======================================"
