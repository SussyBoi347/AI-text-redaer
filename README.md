# AI Camera Reader

A Python app that reads text from a live camera feed and speaks it out loud in a human-like voice.

## What it does
- Captures frames from your webcam.
- Runs OCR (Optical Character Recognition) with Tesseract.
- Speaks newly detected text using your system text-to-speech voice.
- Avoids repeating nearly identical text.

## Setup
1. Install Python 3.10+.
2. Install system package **Tesseract OCR**:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS (Homebrew): `brew install tesseract`
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run
```bash
python app.py
```

Optional arguments:
- `--camera 0` camera index.
- `--ocr-interval 1.2` seconds between OCR attempts.
- `--min-text-length 4` minimum characters before speaking.
- `--similarity-threshold 0.8` skip reading if too similar to the last text.

Press `q` in the preview window to quit.

## Notes
- The voice is provided by your OS speech engine through `pyttsx3`.
- OCR quality improves with bright, steady lighting and clear text.
