"""
jarvis/face_recognition_module.py — Face detection and recognition for J.A.R.V.I.S.
Uses OpenCV + face_recognition library. Falls back gracefully if unavailable.
"""

from __future__ import annotations
import sqlite3
import numpy as np
from typing import List, Tuple, Optional

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import face_recognition
    FR_AVAILABLE = True
except ImportError:
    FR_AVAILABLE = False

import config


class FaceRecognitionModule:
    """Detects and identifies faces using a database of known encodings."""

    def __init__(self):
        self.known_encodings: List[np.ndarray] = []
        self.known_names: List[str] = []
        self._load_from_db()
        if not FR_AVAILABLE:
            print("[Face] face_recognition library not installed. Face ID disabled.")
        if not CV2_AVAILABLE:
            print("[Face] opencv-python not installed. Camera disabled.")

    @property
    def available(self) -> bool:
        return CV2_AVAILABLE and FR_AVAILABLE

    # ── Database I/O ──────────────────────────────────────────────────────────
    def _load_from_db(self):
        """Load stored face encodings from the database."""
        try:
            conn = sqlite3.connect(config.DB_PATH)
            rows = conn.execute("SELECT name, encoding FROM faces").fetchall()
            conn.close()
            self.known_encodings = []
            self.known_names = []
            for name, blob in rows:
                enc = np.frombuffer(blob, dtype=np.float64)
                self.known_encodings.append(enc)
                self.known_names.append(name)
            print(f"[Face] Loaded {len(self.known_names)} known faces")
        except Exception as e:
            print(f"[Face] DB load error: {e}")

    def save_face(self, name: str, encoding: np.ndarray) -> str:
        """Persist a new face encoding to the database."""
        try:
            conn = sqlite3.connect(config.DB_PATH)
            conn.execute(
                "INSERT OR REPLACE INTO faces (name, encoding) VALUES (?, ?)",
                (name, encoding.tobytes())
            )
            conn.commit()
            conn.close()
            self._load_from_db()
            return f"✅ Face '{name}' saved."
        except Exception as e:
            return f"Error saving face: {e}"

    def delete_face(self, name: str) -> str:
        try:
            conn = sqlite3.connect(config.DB_PATH)
            conn.execute("DELETE FROM faces WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            self._load_from_db()
            return f"🗑️  Face '{name}' removed."
        except Exception as e:
            return f"Error: {e}"

    # ── Recognition ───────────────────────────────────────────────────────────
    def identify_faces(self, frame: np.ndarray) -> List[Tuple[Tuple, str]]:
        """
        Given a BGR frame, return [(face_location, name), ...].
        face_location is (top, right, bottom, left) in original frame coords.
        """
        if not self.available:
            return []
        # Downsample for speed
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, locations)

        results = []
        for loc, enc in zip(locations, encodings):
            name = "Unknown"
            if self.known_encodings:
                matches = face_recognition.compare_faces(self.known_encodings, enc, tolerance=0.5)
                dists   = face_recognition.face_distance(self.known_encodings, enc)
                best    = int(np.argmin(dists))
                if matches[best]:
                    name = self.known_names[best]
            # Scale back to original
            top, right, bottom, left = loc
            results.append(((top * 4, right * 4, bottom * 4, left * 4), name))
        return results

    def draw_faces(self, frame: np.ndarray,
                   detections: List[Tuple[Tuple, str]]) -> np.ndarray:
        """Draw bounding boxes and names on frame."""
        for (top, right, bottom, left), name in detections:
            color = (0, 255, 100) if name != "Unknown" else (0, 80, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 28), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 5, bottom - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
        return frame

    def capture_face_from_camera(self, name: str,
                                  cap: Optional[object] = None) -> str:
        """Capture a face from the camera and save it to the database."""
        if not self.available:
            return "Face recognition libraries not available."
        release_after = cap is None
        if cap is None:
            cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if release_after:
            cap.release()
        if not ret:
            return "Could not read from camera."
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            return "No face detected in frame. Please try again."
        return self.save_face(name, encodings[0])
