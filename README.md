# MP4 to GIF Converter

A simple Python script to convert MP4 video files to animated GIFs using FFmpeg.  
Supports trimming, resizing, frame rate adjustment, aspect ratio cropping, and color enhancement.

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
python video-to-gif.py INPUT_FILE [--output OUTPUT_FILE] [--start START] [--end END] [--resize RESIZE] [--fps FPS] [--aspect ASPECT | --ar AR] [--crop-in] [--contrast CONTRAST] [--saturation SATURATION]
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
  Resize parameter. Can be:
  - Scale factor (e.g., `0.5` for 50% size)
  - Pixel dimension (e.g., `800` for 800px max dimension)
  Default: `1.0` (no resize).

- `--fps FPS`  
  Frames per second for the GIF. Default: `10`.

- `--aspect ASPECT` or `--ar AR`  
  Target aspect ratio for the output GIF (e.g., `1:1`, `16:9`, `4:3`). The video will be transformed to this aspect ratio. Optional.

- `--crop-in`  
  When used with `--aspect`/`--ar`, crops the video to the target aspect ratio instead of stretching it. This preserves the original pixel aspect ratio and prevents distortion.

- `--contrast CONTRAST`  
  Contrast adjustment (float). `1.0` = normal, `>1.0` = more contrast, `<1.0` = less contrast. Default: `1.0`.

- `--saturation SATURATION`  
  Saturation adjustment (float). `1.0` = normal, `>1.0` = more saturated, `<1.0` = less saturated. Default: `1.0`.

### Examples

**Basic conversion:**
```bash
python video-to-gif.py "my_video.mp4"
```

**Convert first 5 seconds to half-size GIF at 15 fps:**
```bash
python video-to-gif.py "my_video.mp4" --start 0 --end 5 --resize 0.5 --fps 15
```

**Resize to 600px max dimension with square aspect ratio (cropped, not stretched):**
```bash
python video-to-gif.py "my_video.mp4" --resize 600 --ar 1:1 --crop-in
```

**Enhanced colors with higher contrast and saturation:**
```bash
python video-to-gif.py "my_video.mp4" --contrast 1.3 --saturation 1.2
```

**Complete example with all features:**
```bash
python video-to-gif.py "input.mp4" --start 10 --end 20 --resize 800 --fps 12 --ar 16:9 --crop-in --contrast 1.2 --saturation 1.1
```

## Feature Details

### Resize Options
- **Scale factors**: Values like `0.5`, `1.5`, `2.0` resize proportionally
- **Pixel dimensions**: Integer values ≥10 (e.g., `600`, `800`, `1200`) set the maximum dimension while preserving aspect ratio

### Aspect Ratio Handling
- **Without `--crop-in`**: Stretches/squashes the video to fit the target aspect ratio
- **With `--crop-in`**: Crops the video to fit the target aspect ratio without distortion

### Color Enhancement
- **Contrast**: `1.5` = 50% more contrast, `0.7` = 30% less contrast
- **Saturation**: `1.3` = 30% more saturated, `0.5` = 50% less saturated, `0.0` = grayscale

### Video Aspect Ratio Issues
This script automatically handles videos with unusual aspect ratio metadata:

- **Videos that appear square but have rectangular dimensions**: The script detects when a video has a display aspect ratio (DAR) of 1:1 but rectangular pixel dimensions. It automatically produces a square GIF that matches what you see in video players.

- **Pixel aspect ratio (PAR) correction**: Videos with non-square pixels are correctly handled to ensure the output GIF maintains the same visual appearance as the original video.

## Output Filename Convention

When no output filename is specified, the script generates descriptive filenames:

- `video_50pct_10fps.gif` - 50% scale, 10 fps
- `video_800px_15fps_16x9_cropped.gif` - 800px max, 15 fps, 16:9 aspect, cropped
- `video_100pct_10fps_c13_s12.gif` - normal size, 10 fps, 1.3 contrast, 1.2 saturation

## Notes

- **Paths with spaces**: Always use quotes around file paths with spaces or special characters.
- **Dependencies**: This script uses only Python's standard library and FFmpeg.
- **Performance**: Larger files and higher quality settings will take longer to process.

## License

MIT License
