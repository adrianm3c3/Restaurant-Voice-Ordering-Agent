#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "======================================"
echo " Spec Regeneration Check"
echo "======================================"

if [ ! -f "docs/SPEC.md" ]; then
  echo "Missing docs/SPEC.md"
  exit 1
fi

if [ ! -f "docs/STORIES.md" ]; then
  echo "Missing docs/STORIES.md"
  exit 1
fi

if [ ! -f "scripts/regenerate_prompt.md" ]; then
  echo "Missing scripts/regenerate_prompt.md"
  exit 1
fi

{
  echo "Spec regeneration artifact check"
  echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "Found:"
  echo "- docs/SPEC.md"
  echo "- docs/STORIES.md"
  echo "- scripts/regenerate_prompt.md"
  echo
  echo "NOTE:"
  echo "This local script checks that regeneration artifacts exist."
  echo "Use the official course template version if provided."
} > reports/regeneration.txt

echo "Regeneration artifact check complete."
echo "Report written to reports/regeneration.txt"
