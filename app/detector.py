"""AI CAM detection engine.

Uses OpenCV's bundled Haar cascade classifiers to detect faces (and eyes within
those faces) in an image. The cascades ship with the ``opencv-python-headless``
wheel, so no external model download is required at runtime.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from functools import lru_cache

import cv2
import numpy as np


@dataclass
class Detection:
    """A single detected face plus any eyes found inside it."""

    x: int
    y: int
    width: int
    height: int
    eyes: list[dict[str, int]] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "eyes": self.eyes,
        }


@dataclass
class DetectionResult:
    detections: list[Detection]
    image_width: int
    image_height: int
    annotated_png_base64: str

    def as_dict(self) -> dict[str, object]:
        return {
            "count": len(self.detections),
            "imageWidth": self.image_width,
            "imageHeight": self.image_height,
            "detections": [d.as_dict() for d in self.detections],
            "annotatedImage": f"data:image/png;base64,{self.annotated_png_base64}",
        }


@lru_cache(maxsize=1)
def _face_cascade() -> cv2.CascadeClassifier:
    path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise RuntimeError(f"Failed to load face cascade from {path}")
    return cascade


@lru_cache(maxsize=1)
def _eye_cascade() -> cv2.CascadeClassifier:
    path = cv2.data.haarcascades + "haarcascade_eye.xml"
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise RuntimeError(f"Failed to load eye cascade from {path}")
    return cascade


def decode_image(raw: bytes) -> np.ndarray:
    """Decode raw image bytes into a BGR OpenCV image."""
    buffer = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image. Provide a valid JPEG/PNG.")
    return image


def detect(image: np.ndarray) -> DetectionResult:
    """Run face + eye detection and produce an annotated PNG."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = _face_cascade().detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(40, 40),
    )

    annotated = image.copy()
    detections: list[Detection] = []

    for (x, y, w, h) in faces:
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 200, 255), 3)
        cv2.putText(
            annotated,
            "face",
            (x, max(0, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 200, 255),
            2,
            cv2.LINE_AA,
        )

        face_roi = gray[y : y + h, x : x + w]
        eyes = _eye_cascade().detectMultiScale(
            face_roi,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(15, 15),
        )
        eye_list: list[dict[str, int]] = []
        for (ex, ey, ew, eh) in eyes:
            abs_ex, abs_ey = int(x + ex), int(y + ey)
            cv2.rectangle(
                annotated,
                (abs_ex, abs_ey),
                (abs_ex + ew, abs_ey + eh),
                (80, 255, 80),
                2,
            )
            eye_list.append(
                {"x": abs_ex, "y": abs_ey, "width": int(ew), "height": int(eh)}
            )

        detections.append(
            Detection(x=int(x), y=int(y), width=int(w), height=int(h), eyes=eye_list)
        )

    ok, encoded = cv2.imencode(".png", annotated)
    if not ok:
        raise RuntimeError("Failed to encode annotated image")
    annotated_b64 = base64.b64encode(encoded.tobytes()).decode("ascii")

    height, width = image.shape[:2]
    return DetectionResult(
        detections=detections,
        image_width=int(width),
        image_height=int(height),
        annotated_png_base64=annotated_b64,
    )
