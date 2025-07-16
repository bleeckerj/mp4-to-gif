# MP4 to GIF Converter

A simple Python script to convert MP4 video files to animated GIFs using FFmpeg.
Supports trimming, resizing, frame rate adjustment, and aspect ratio cropping.

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
python video-to-gif.py INPUT_FILE [--output OUTPUT_FILE] [--start START] [--end END] [--resize RESIZE] [--fps FPS] [--aspect ASPECT]
```

### Arguments

- `INPUT_FILE`  
  Path to the input MP4 file.

- `--output OUTPUT_FILE`  
  Path to the output GIF file. Defaults to the same name as the input with `.gif` extension (plus parameter info).

- `--start START`  
  Start time in seconds (float). Optional.

- `--end END`  
  End time in seconds (float). Optional.

- `--resize RESIZE`  
  Resize factor (e.g., `0.5` for 50% size). Default: `1.0`.

- `--fps FPS`  
  Frames per second for the GIF. Default: `10`.

- `--aspect ASPECT`  
  Target aspect ratio for the output GIF (e.g., `1:1`, `16:9`, `4:3`). The video will be center-cropped to this aspect ratio before resizing. Optional.

### Example

Convert the first 5 seconds of a video to a half-size, 16:9 GIF at 15 fps:

```bash
python video-to-gif.py "/Users/julian/Movies/My Video.mp4" --output "output.gif" --start 0 --end 5 --resize 0.5 --fps 15 --aspect 16:9
```

## Video Aspect Ratio Handling

This script can handle videos with unusual aspect ratio metadata:

- **Videos that appear square but have rectangular dimensions**: The script detects when a video has a display aspect ratio (DAR) of 1:1 but the actual pixel dimensions are rectangular. In these cases, the script will automatically produce a square GIF that matches what you see in video players.

- **Pixel aspect ratio (PAR) correction**: Videos with non-square pixels are correctly handled to ensure the output GIF maintains the same visual appearance as the original video.

- **Forcing a specific aspect ratio**: Using the `--aspect` parameter allows you to create GIFs with specific aspect ratios like square (1:1) or widescreen (16:9), regardless of the source video's dimensions.

## Notes

- **Paths with spaces:**  
  Always use quotes around file paths with spaces or special characters.

- **Dependencies:**  
  This script uses only Python's standard library and FFmpeg.

## License

MIT License
