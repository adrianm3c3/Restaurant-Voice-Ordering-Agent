 Reproduce

## Goal

This document explains how to reproduce the Restaurant Voice Ordering Agent from a clean clone.

## Hardware Profile Used During Development

| Item | Value |
|---|---|
| OS | Windows 11 |
| Python | 3.10 |
| Container base | `python:3.10-slim` |
| Docker | Docker Desktop with Docker Compose |
| CPU | x86_64 |
| GPU | Not required for Docker path |
| Network | Required for dependency/model downloads and optional LLM endpoint |

## Required Software

- Git
- Docker Desktop
- Docker Compose
- Internet access

## Fresh Clone Steps

```bash
git clone https://github.com/adrianm3c3/Restaurant-Voice-Ordering-Agent.git
cd ResturauntProject
cp .env.example .env
docker compose up --build

