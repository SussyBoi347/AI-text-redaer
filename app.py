import argparse
import queue
import threading
import time
from dataclasses import dataclass

import cv2
import pyttsx3
import pytesseract


@dataclass
class AppConfig:
    camera_index: int
    ocr_interval: float
    min_text_length: int
    similarity_threshold: float


class TextSpeaker:
    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        self._q: "queue.Queue[str]" = queue.Queue()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def say(self, text: str) -> None:
        if text.strip():
            self._q.put(text)

    def close(self) -> None:
        self._stop.set()
        self._q.put("")
        self._thread.join(timeout=2)

    def _worker(self) -> None:
        while not self._stop.is_set():
            text = self._q.get()
            if self._stop.is_set():
                break
            if text.strip():
                self._engine.say(text)
                self._engine.runAndWait()


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def jaccard_similarity(a: str, b: str) -> float:
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def extract_text(frame) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    filtered = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    raw_text = pytesseract.image_to_string(thresh)
    return normalize_text(raw_text)


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(
        description="Read text from a camera feed and speak it out loud."
    )
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument(
        "--ocr-interval",
        type=float,
        default=1.2,
        help="Seconds between OCR attempts (default: 1.2)",
    )
    parser.add_argument(
        "--min-text-length",
        type=int,
        default=4,
        help="Minimum number of characters to speak (default: 4)",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.8,
        help="Skip reading if text is too similar to previous output (default: 0.8)",
    )
    args = parser.parse_args()
    return AppConfig(
        camera_index=args.camera,
        ocr_interval=args.ocr_interval,
        min_text_length=args.min_text_length,
        similarity_threshold=args.similarity_threshold,
    )


def main() -> None:
    config = parse_args()
    cap = cv2.VideoCapture(config.camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {config.camera_index}")

    speaker = TextSpeaker()
    speaker.start()

    last_text = ""
    last_ocr = 0.0

    print("Press 'q' in the preview window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Warning: failed to read frame from camera")
                continue

            cv2.imshow("AI Camera Reader", frame)

            now = time.time()
            if now - last_ocr >= config.ocr_interval:
                last_ocr = now
                text = extract_text(frame)
                if len(text) >= config.min_text_length:
                    similarity = jaccard_similarity(text, last_text)
                    if similarity < config.similarity_threshold:
                        print(f"Detected: {text}")
                        speaker.say(text)
                        last_text = text

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        speaker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
