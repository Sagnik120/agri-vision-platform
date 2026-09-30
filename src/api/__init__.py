"""
HTTP API layer for the Next.js frontend (and the future mobile app).

Thin adapter only: every decision still lives in zone1_edge / zone2_cloud /
zone3_memory. Run with:

    .venv/bin/uvicorn src.api.main:app --reload --port 8000
"""
