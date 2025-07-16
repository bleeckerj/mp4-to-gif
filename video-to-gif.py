import os
import sys
import subprocess

def parse_aspect(aspect_str):
    """Parse aspect ratio string like '16:9' or '1:1' and return (w, h) as floats."""
    try:
        w, h = aspect_str.split(":")
        return float(w), float(h)
    except Exception:
        raise ValueError("Aspect ratio must be in the format W:H, e.g., 16:9 or 1:1")

def mp4_to_gif(input_path, output_path=None, start_time=None, end_time=None, resize_factor=1.0, fps=10, aspect=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    
    # Determine output filename if not specified
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        resize_pct = int(resize_factor * 100)
        output_path = f"{base}_{resize_pct}pct_{fps}fps.gif"
        if aspect:
            aspect_str = aspect.replace(":", "x")
            output_path = f"{base}_{resize_pct}pct_{fps}fps_{aspect_str}.gif"
    
    filters = []
    
    # Add aspect ratio crop if specified
    if aspect:
        w_ratio, h_ratio = parse_aspect(aspect)
        # Center crop to desired aspect ratio
        filters.append(f"crop='if(gt(a,{w_ratio}/{h_ratio}),ih*{w_ratio}/{h_ratio},iw)':'if(gt(a,{w_ratio}/{h_ratio}),ih,iw*{h_ratio}/{w_ratio})'")
    
    # Add resizing if needed
    if resize_factor != 1.0:
        filters.append(f"scale=iw*{resize_factor}:ih*{resize_factor}")
    
    # Add fps filter
    filters.append(f"fps={fps}")
    
    # Combine filters
    filter_string = ",".join(filters)
    
    # Build FFmpeg command
    cmd = ["ffmpeg", "-y"]  # -y to overwrite output files
    
    # Add start time if specified
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    
    # Add input file
    cmd.extend(["-i", input_path])
    
    # Add end time/duration if specified
    if end_time is not None:
        if start_time is not None:
            duration = end_time - start_time
            cmd.extend(["-t", str(duration)])
        else:
            cmd.extend(["-to", str(end_time)])
    
    # Add filters
    if filters:
        cmd.extend(["-vf", filter_string])
    
    # Output options and file
    cmd.append(output_path)
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        print(f"GIF saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e.stderr}")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MP4 to animated GIF")
    parser.add_argument("input", help="Path to input MP4 file")
    parser.add_argument("--output", help="Path to output GIF file")
    parser.add_argument("--start", type=float, help="Start time in seconds")
    parser.add_argument("--end", type=float, help="End time in seconds")
    parser.add_argument("--resize", type=float, default=1.0, help="Resize factor (e.g. 0.5 for 50%)")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the GIF")
    parser.add_argument("--aspect", type=str, help="Target aspect ratio (e.g. 1:1, 16:9, 4:3)")

    args = parser.parse_args()

    mp4_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps, args.aspect)
