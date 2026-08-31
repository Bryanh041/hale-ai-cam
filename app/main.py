"""CAM5x AI CAM — FastAPI application.

Serves the single-page web UI and exposes a JSON detection API that runs
OpenCV face/eye detection on uploaded frames.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import detector

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="CAM5x AI CAM", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "cam5x-ai-cam", "version": app.version}


@app.post("/api/detect")
async def detect_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty upload.")
    try:
        image = detector.decode_image(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = detector.detect(image)
    return JSONResponse(result.as_dict())


app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
