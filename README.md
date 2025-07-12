# MP4 to GIF Converter

A simple Python script to convert MP4 video files to animated GIFs using FFmpeg.
Supports trimming, resizing, and frame rate adjustment.

## Requirements

- Python 3.6+
- [FFmpeg](https://ffmpeg.org/) installed and available in your system PATH

## Installation

1. **Clone this repository or copy the script.**
2. **Install FFmpeg:**

   On macOS (with Homebrew):
   ```bash
   brew install ffmpeg
   ```

   On Ubuntu/Debian:
   ```bash
   sudo apt install ffmpeg
   ```

3. **(Optional) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

## Usage

```bash
python video-to-gif.py INPUT_FILE [--output OUTPUT_FILE] [--start START] [--end END] [--resize RESIZE] [--fps FPS]
```

### Arguments

- `INPUT_FILE`  
  Path to the input MP4 file.

- `--output OUTPUT_FILE`  
  Path to the output GIF file. Defaults to the same name as the input with `.gif` extension.

- `--start START`  
  Start time in seconds (float). Optional.

- `--end END`  
  End time in seconds (float). Optional.

- `--resize RESIZE`  
  Resize factor (e.g., `0.5` for 50% size). Default: `1.0`.

- `--fps FPS`  
  Frames per second for the GIF. Default: `10`.

### Example

Convert the first 5 seconds of a video to a half-size GIF at 15 fps:

```bash
python video-to-gif.py "/Users/julian/Movies/My Video.mp4" --output "output.gif" --start 0 --end 5 --resize 0.5 --fps 15
```

## Notes

- **Paths with spaces:**  
  Always use quotes around file paths with spaces or special characters.

- **Dependencies:**  
  This script uses only Python's standard library and FFmpeg.

## License

MIT License
