# hale-ai-cam

CAM5x AI CAM — a self-contained AI camera web app that performs real-time
face and eye detection in the browser using OpenCV Haar cascades.

## Stack

- **Backend:** FastAPI + Uvicorn (`app/`)
- **Detection:** OpenCV (`opencv-python-headless`) Haar cascades — no external model download required
- **Frontend:** static single-page UI served by FastAPI (`web/`)

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000.

- **Start camera** → **Capture & analyze** runs detection on a live webcam frame.
- **Analyze sample image** runs detection on the bundled sample (works without a camera).

## API

| Method | Path          | Description                                              |
| ------ | ------------- | ------------------------------------------------------- |
| GET    | `/api/health` | Service health probe.                                   |
| POST   | `/api/detect` | Multipart `file` upload → JSON with faces, eyes, and an annotated image. |

Example:

```bash
curl -F "file=@web/sample.jpg" http://localhost:8000/api/detect
```

## Cloud Agent environment

`.cursor/environment.json` installs dependencies into `.venv` and runs the API
in the `api` terminal on port `8000`.
