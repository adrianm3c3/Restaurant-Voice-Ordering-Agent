# Benchmarks

## Overview

This document records benchmark and smoke-test results for the Restaurant Voice Ordering Agent.

The benchmark focus is the Flask API endpoint:

POST /api/chat

This endpoint is used for grading because it exercises the same restaurant agent logic as the Twilio voice path without requiring a phone call, ngrok, or a Twilio account.

## Hardware / Runtime Environment

| Item | Value |
|---|---|
| Development OS | Windows 11 |
| Container runtime | Docker Desktop |
| Container base image | python:3.10-slim |
| Python version | 3.10 |
| Server | Flask development server |
| GPU required | No |
| External services | Optional OpenAI-compatible LLM endpoint for live RAG generation |

## Smoke Test Methodology

The smoke test verifies that the system can:

1. Build the Docker image.
2. Start the Flask server through Docker Compose.
3. Respond to GET /health.
4. Accept an order through POST /api/chat.
5. Preserve session state across multiple API calls.
6. Return an order total.

## Docker Smoke Test

Command:

docker compose up --build

Observed result:

PASS

Evidence file:

reports/docker_smoke_test.txt

## Health Check

Command:

Invoke-RestMethod http://127.0.0.1:5000/health

Expected response:

{
  "status": "ok"
}

Observed result:

PASS

## API Order Test

Command:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"benchmark-demo","text":"I want a large pepperoni pizza"}'

Expected reply:

Added 1 large pepperoni pizza with hand tossed.

Observed result:

PASS

## API Session Memory Test

Command:

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:5000/api/chat" `
  -ContentType "application/json" `
  -Body '{"session_id":"benchmark-demo","text":"what is my total"}'

Expected reply:

Your total is $14.04.

Observed result:

PASS

## Automated Test Benchmark

Command:

pytest tests --junitxml=reports/user_stories.xml --cov=src --cov-report=xml:reports/coverage.xml --cov-report=html:reports/coverage_html -v

Observed result:

22 passed

Observed runtime:

37.37 seconds

Generated reports:

reports/user_stories.xml  
reports/coverage.xml  
reports/coverage_html/

## Headline Numbers

| Metric | Result |
|---|---:|
| Full test suite | 22 passed |
| User story tests | Passing |
| API integration tests | Passing |
| RAG integration tests | Passing |
| Docker health check | HTTP 200 |
| API smoke test error rate | 0% observed |
| Docker build after cleanup | Approximately 250 seconds observed |

## Load Test Target

| Target | Value |
|---|---:|
| Endpoint | POST /api/chat |
| Request rate | 10 requests/second |
| Duration | 60 seconds |
| Error rate | Under 5% |

## Planned Load Test Command

make loadtest

or directly with Locust:

locust -f tests/load/locustfile.py --headless -u 10 -r 2 -t 60s --host=http://localhost:5000

## Raw Timing / Report Artifacts

Current report artifacts:

reports/docker_smoke_test.txt  
reports/docker_compose_ps.txt  
reports/docker_logs.txt  
reports/user_stories.xml  
reports/coverage.xml  
reports/coverage_html/

Planned load-test report artifact:

reports/benchmarks.json

## Notes

The current benchmark evidence is based on smoke testing and automated test execution. A formal load test file should be added under:

tests/load/locustfile.py